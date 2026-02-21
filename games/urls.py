from django.urls import path

from .views import GameDetailView, GameListView, DashboardView

app_name = 'games'

urlpatterns = [
    path('<int:pk>/', GameDetailView.as_view(), name='game-detail'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', GameListView.as_view(), name='game-list'),
]
