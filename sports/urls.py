
from django.urls import path
from . import views

urlpatterns = [
    path('players/', views.players_list, name='players_list'),
]
