from django.urls import path
from . import views

urlpatterns = [
    path('', views.calcolatore_view, name='calcolatore'),
    path('api/calcolatore/', views.calcolatore_api, name='calcolatore_api'),
]
