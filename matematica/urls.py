from django.urls import path
from . import views

urlpatterns = [
    path('', views.calcolatore_view, name='calcolatore'),
    path('steam-reformer/', views.steam_reformer_view, name='steam_reformer'),
    path('bobyqa/', views.bobyqa_view, name='bobyqa'),
    path('steam-reformer-simulation/', views.steam_reformer_simulation_view, name='steam_reformer_simulation'),
    path('electric-steam-reformer-simulation/', views.electric_steam_reformer_simulation_view, name='electric_steam_reformer_simulation'),
    
    # API endpoints
    path('api/calcolatore/', views.calcolatore_api, name='calcolatore_api'),
    path('api/steam-reformer/', views.steam_reformer_api, name='steam_reformer_api'),
    path('api/steam-reformer/calcoli/', views.steam_reformer_calcoli_api, name='steam_reformer_calcoli_api'),
]
