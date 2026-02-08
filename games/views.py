from django.views.generic import DetailView, ListView

from .models import Game
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
