from django.urls import path
from . import views

urlpatterns = [
    path('', views.scraper_buscar, name='scraper_buscar'),
]