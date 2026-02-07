from django.urls import path

from .views import GameDetailView, GameListView

app_name = 'games'

urlpatterns = [
    path('<int:pk>/', GameDetailView.as_view(), name='game-detail'),
    path('', GameListView.as_view(), name='game-list'),
]
