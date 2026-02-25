import json
import os
import uuid
from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, ListView, TemplateView

from core.models import BackgroundTask

from .models import Game, GameActivity
from .tasks import import_steam_games


class GameListView(ListView):
    model = Game
    template_name = 'games/game_list.html'
    context_object_name = 'games'
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(raw_data__short_description__icontains=search_query)
            )

        order_by = self.request.GET.get('order_by')
        ordering_fields = {
            'playtime_desc': '-playtime',
            'playtime_asc': 'playtime',
            'name': 'name',
            'last_played': '-raw_data__rtime_last_played',
        }

        if order_by in ordering_fields:
            queryset = queryset.order_by(ordering_fields[order_by])
        else:
            queryset = queryset.order_by('-playtime')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['active_task_id'] = ""

        if self.request.user.is_authenticated:
            active_task = self.request.user.background_tasks.filter(
                task_name='STEAM_GAMES_IMPORT',
                status=BackgroundTask.Status.PENDING
            ).first()

            if active_task:
                context['active_task_id'] = active_task.task_id

        context['search_query'] = self.request.GET.get('q', '')
        context['order_by'] = self.request.GET.get('order_by', 'playtime_desc')

        return context


class GameDetailView(DetailView):
    model = Game
    template_name = 'games/game_detail.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_activities = self.object.history.all().order_by('created_at')

        dates = []
        playtimes = []

        for activity in game_activities:
            dates.append(activity.created_at.strftime('%m %d %Y'))
            playtimes.append(activity.playtime)

        context['graph_dates'] = json.dumps(dates)
        context['graph_playtimes'] = json.dumps(playtimes)

        return context


class DashboardView(TemplateView):
    template_name = 'games/dashboard.html'
    context_object_name = 'dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playtime_stats = GameActivity.objects.aggregate(
            total_playtime=models.Sum('playtime')
        )

        mins_played = playtime_stats['total_playtime'] or 0.0

        context['total_playtime'] = mins_played / 60
        context['top_played'] = Game.objects.order_by('-playtime')[:5]

        longest_session = GameActivity.objects.order_by('-playtime').first()

        if longest_session:
            context['longest_session'] = {
                'game': longest_session.game,
                'playtime': longest_session.playtime / 60
            }
        else:
            context['longest_session'] = {
                'game': 'No sessions for this time period',
                'playtime': 0.0
            }

        avg_session = GameActivity.objects.aggregate(
            avg_playtime=models.Avg('playtime')
        )

        mins_avg = avg_session['avg_playtime'] or 0.0

        context['avg_session'] = mins_avg / 60

        month_ago = timezone.now() - timedelta(days=30)
        context['games_last_month'] = GameActivity.objects.filter(
            created_at__gte=month_ago
        ).values('game').distinct().count()

        return context


@require_POST
def start_import_task_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    steam_id = os.environ.get('STEAM_ID')
    api_key = os.environ.get('STEAM_API_KEY')

    temp_task_id = str(uuid.uuid4())

    db_task_record = BackgroundTask.objects.create(
        user=request.user,
        task_id=temp_task_id,
        task_name='STEAM_GAMES_IMPORT',
        status=BackgroundTask.Status.PENDING
    )

    celery_task = import_steam_games.delay(steam_id, api_key, db_task_record.id)

    db_task_record.task_id = celery_task.id
    db_task_record.save(update_fields=['task_id'])

    return JsonResponse({
        'message': 'Import task started',
        'task_id': celery_task.id
    })


@require_GET
def check_import_task_status_view(request, task_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if not request.user.background_tasks.filter(task_id=task_id).exists():
        return JsonResponse({'error': 'Task not found'}, status=404)

    celery_task = import_steam_games.AsyncResult(task_id)

    result = celery_task.result if celery_task.ready() else None

    return JsonResponse({
        'task_id': celery_task.id,
        'status': celery_task.status,
        'result': result
    })
