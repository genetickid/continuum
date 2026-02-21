import json
from datetime import timedelta

from django.views.generic import DetailView, ListView, TemplateView
from django.db import models
from django.utils import timezone

from .models import Game, GameActivity
from django.db.models import Q


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
