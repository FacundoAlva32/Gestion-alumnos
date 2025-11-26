import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from urllib.parse import quote
import re
import time
from .forms import BusquedaForm

@login_required
def scraper_buscar(request):
    resultados = []
    palabra_clave = ""
    form = BusquedaForm()
    
    if request.method == 'POST':
        form = BusquedaForm(request.POST)
        if form.is_valid():
            palabra_clave = form.cleaned_data['palabra_clave']
            email_destino = form.cleaned_data['email_destino']
            
            try:
                # URL encode para caracteres especiales
                search_term = quote(palabra_clave)
                
                # Buscar en Wikipedia en español usando API
                search_url = "https://es.wikipedia.org/w/api.php"
                params = {
                    'action': 'query',
                    'list': 'search',
                    'srsearch': palabra_clave,
                    'format': 'json',
                    'srlimit': 10,
                    'srprop': 'size|wordcount|timestamp',  # Más propiedades
                    'utf8': 1
                }
                
                headers = {
                    'User-Agent': 'SistemaEducativo/1.0 (https://mi-sistema.com; contacto@mi-sistema.com)'
                }
                
                # Hacer búsqueda en Wikipedia con timeout
                try:
                    response = requests.get(
                        search_url, 
                        params=params, 
                        headers=headers,
                        timeout=10  # 10 segundos de timeout
                    )
                    response.raise_for_status()  # Lanza excepción para códigos 4xx/5xx
                    
                except requests.exceptions.Timeout:
                    messages.error(request, '⏰ Timeout: Wikipedia no respondió a tiempo. Intenta nuevamente.')
                    return render(request, 'scraper/buscar.html', {
                        'form': form,
                        'resultados': resultados,
                        'palabra_clave': palabra_clave,
                        'total_resultados': len(resultados)
                    })
                    
                except requests.exceptions.ConnectionError:
                    messages.error(request, '🔌 Error de conexión: No se pudo conectar con Wikipedia. Verifica tu conexión a internet.')
                    return render(request, 'scraper/buscar.html', {
                        'form': form,
                        'resultados': resultados,
                        'palabra_clave': palabra_clave,
                        'total_resultados': len(resultados)
                    })
                    
                except requests.exceptions.RequestException as e:
                    messages.error(request, f'❌ Error de red: {str(e)}')
                    return render(request, 'scraper/buscar.html', {
                        'form': form,
                        'resultados': resultados,
                        'palabra_clave': palabra_clave,
                        'total_resultados': len(resultados)
                    })
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verificar si hay error en la respuesta de la API
                    if 'error' in data:
                        messages.error(request, f'❌ Error de Wikipedia: {data["error"]["info"]}')
                        return render(request, 'scraper/buscar.html', {
                            'form': form,
                            'resultados': resultados,
                            'palabra_clave': palabra_clave,
                            'total_resultados': len(resultados)
                        })
                    
                    search_results = data.get('query', {}).get('search', [])
                    
                    if search_results:
                        for result in search_results:
                            title = result.get('title', '')
                            snippet = result.get('snippet', '')
                            
                            # Limpiar el snippet de HTML
                            snippet_clean = re.sub(r'<[^>]+>', '', snippet)
                            snippet_clean = snippet_clean.replace('&quot;', '"').replace('&nbsp;', ' ')
                            snippet_clean = snippet_clean.replace('&#39;', "'").replace('&amp;', '&')
                            
                            # Construir URL del artículo
                            article_url = f"https://es.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
                            
                            # Obtener más detalles del artículo (con manejo de errores)
                            extract = snippet_clean
                            try:
                                article_response = requests.get(
                                    f"https://es.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'))}",
                                    headers=headers,
                                    timeout=5
                                )
                                if article_response.status_code == 200:
                                    article_data = article_response.json()
                                    if article_data.get('extract'):
                                        extract_text = article_data.get('extract', '')
                                        if len(extract_text) > 400:
                                            extract = extract_text[:400] + '...'
                                        else:
                                            extract = extract_text
                                # Pequeña pausa para ser amable con el servidor
                                time.sleep(0.1)
                            except:
                                # Si falla, usamos el snippet de la búsqueda
                                pass
                            
                            # Formatear fecha si existe
                            fecha = result.get('timestamp', '')
                            if fecha:
                                try:
                                    # Convertir de formato ISO a más legible
                                    fecha = fecha[:10]  # YYYY-MM-DD
                                except:
                                    fecha = ''
                            
                            resultados.append({
                                'titulo': title,
                                'url': article_url,
                                'resumen': extract,
                                'fuente': 'Wikipedia',
                                'fecha': fecha,
                                'tamaño': result.get('size', 0),
                                'palabras': result.get('wordcount', 0)
                            })
                        
                        messages.success(request, f'✅ Se encontraron {len(resultados)} resultados para "{palabra_clave}"')
                        
                        # Enviar email si se proporcionó un email
                        if email_destino:
                            try:
                                enviar_resultados_por_email(email_destino, palabra_clave, resultados)
                                messages.info(request, f'📧 Resultados enviados a: {email_destino}')
                            except Exception as e:
                                messages.warning(request, f'⚠️ No se pudo enviar el email: {str(e)}')
                    
                    else:
                        messages.warning(request, f'❌ No se encontraron resultados para "{palabra_clave}"')
                        messages.info(request, '💡 Sugerencia: Intenta con términos más generales o revisa la ortografía')
                
                else:
                    messages.error(request, f'❌ Error HTTP {response.status_code} al conectarse con Wikipedia.')
            
            except Exception as e:
                messages.error(request, f'❌ Error inesperado: {str(e)}')
    
    return render(request, 'scraper/buscar.html', {
        'form': form,
        'resultados': resultados,
        'palabra_clave': palabra_clave,
        'total_resultados': len(resultados)
    })

def enviar_resultados_por_email(destinatario, palabra_clave, resultados):
    """Función para enviar resultados por email usando Brevo"""
    try:
        asunto = f"📚 Resultados de Wikipedia: {palabra_clave}"
        
        # Crear contenido del email
        mensaje = f"""Resultados de búsqueda en Wikipedia para '{palabra_clave}':

🔍 Término buscado: {palabra_clave}
📊 Total de resultados: {len(resultados)}

"""
        
        for i, resultado in enumerate(resultados, 1):
            mensaje += f"""
{i}. {resultado['titulo']}
   📖 Resumen: {resultado['resumen'][:200]}...
   🔗 Enlace: {resultado['url']}
   📅 Fecha: {resultado['fecha'] if resultado['fecha'] else 'No disponible'}
   ---

"""
        
        mensaje += f"""
---
📋 Este email fue generado automáticamente por el Sistema de Gestión de Alumnos.
🌐 Fuente: Wikipedia en español
💻 Enviado mediante Brevo
"""

        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [destinatario],
            fail_silently=False,
        )
        return True
        
    except Exception as e:
        print(f"Error enviando email con Brevo: {e}")
        return False