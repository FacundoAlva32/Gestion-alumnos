from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from usuarios import views as usuario_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', usuario_views.dashboard_view, name='dashboard'),  # Esta es la URL del dashboard
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', usuario_views.registro_view, name='registro'),
    path('alumnos/', include('alumnos.urls')),
    path('scraper/', include('scraper.urls')),
]