from django.urls import path
from . import views

urlpatterns = [
    path('', views.calcolatore_view, name='calcolatore'),
]
