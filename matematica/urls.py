from django.urls import path
from . import views
from .views import vessel_simulation_view, vessel_api
from .views import (
    equation_part_list_view,
    equation_part_create_view,
    equation_part_detail_view,
    equation_part_test_view
)

urlpatterns = [
    path('', views.calcolatore_view, name='calcolatore'),
    path('steam-reformer/', views.steam_reformer_view, name='steam_reformer'),
    path('bobyqa/', views.bobyqa_view, name='bobyqa'),
    path('steam-reformer-simulation/', views.steam_reformer_simulation_view, name='steam_reformer_simulation'),
    path('electric-steam-reformer-simulation/', views.electric_steam_reformer_simulation_view, name='electric_steam_reformer_simulation'),
    path('vessel-simulation/', vessel_simulation_view, name='vessel_simulation'),
    
    # API endpoints
    path('api/calcolatore/', views.calcolatore_api, name='calcolatore_api'),
    path('api/steam-reformer/', views.steam_reformer_api, name='steam_reformer_api'),
    path('api/steam-reformer/calcoli/', views.steam_reformer_calcoli_api, name='steam_reformer_calcoli_api'),
    path('api/vessel/', vessel_api, name='vessel_api'),

    path('parts/', equation_part_list_view, name='equation_part_list'),
    path('parts/new/', equation_part_create_view, name='equation_part_create'),
    path('parts/<int:pk>/', equation_part_detail_view, name='equation_part_detail'),
    path('parts/test/', equation_part_test_view, name='equation_part_test'),
]
