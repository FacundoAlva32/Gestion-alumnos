from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from usuarios import views as usuario_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', usuario_views.pagina_inicio, name='inicio'),  # ← Cambia esta línea
    path('dashboard/', usuario_views.dashboard_view, name='dashboard'),  # ← Dashboard separado
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='inicio'), name='logout'),  # ← Añade next_page
    path('registro/', usuario_views.registro_view, name='registro'),
    path('alumnos/', include('alumnos.urls')),
    path('scraper/', include('scraper.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)