from django.urls import path
from . import views

urlpatterns = [
    path('', views.calcolatore_view, name='calcolatore'),
    path('steam-reformer/', views.steam_reformer_view, name='steam_reformer'),
    path('bobyqa/', views.bobyqa_view, name='bobyqa'), 
    
    # API endpoints
    path('api/calcolatore/', views.calcolatore_api, name='calcolatore_api'),
    path('api/steam-reformer/', views.steam_reformer_api, name='steam_reformer_api'),
    path('api/steam-reformer/calcoli/', views.steam_reformer_calcoli_api, name='steam_reformer_calcoli_api'),
]
