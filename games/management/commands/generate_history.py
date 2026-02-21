from datetime import timedelta
import random
from django.core.management.base import BaseCommand
from django.utils import timezone

from games.models import Game, GameActivity


class Command(BaseCommand):
    help = 'Generate fake play history for the past 30 days based on games playtime.'

    def handle(self, *args, **kwargs):
        GameActivity.objects.all().delete()
        games = Game.objects.filter(playtime__gt=0.1)
        game_activities = []
        now = timezone.now()

        for game in games:
            total_playtime_mins = game.playtime * 60
            month_limit_mins = 100 * 60
            mins_remaining = min(total_playtime_mins, month_limit_mins)

            for days_count in range(30):
                if mins_remaining <= 0:
                    break

                if random.random() > 0.2:
                    continue

                session_mins = min(mins_remaining, random.randint(10, 180))
                mins_remaining -= session_mins

                past_date = (now - timedelta(days=days_count)).replace(
                    hour=random.randint(10, 23),
                    minute=random.randint(0, 59)
                )

                game_activities.append(
                    GameActivity(
                        game=game,
                        playtime=session_mins,
                        created_at=past_date,
                        updated_at=past_date
                    )
                )

        if game_activities:
            GameActivity.objects.bulk_create(game_activities, batch_size=500)
