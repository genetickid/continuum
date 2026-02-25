from django.urls import path

from .views import DashboardView, GameDetailView, GameListView, start_import_task_view, check_import_task_status_view

app_name = 'games'

urlpatterns = [
    path('<int:pk>/', GameDetailView.as_view(), name='game-detail'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('import-start/', start_import_task_view, name='import_start'),
    path('import-status/<str:task_id>/', check_import_task_status_view, name='import_status'),
    path('', GameListView.as_view(), name='game-list'),
]
