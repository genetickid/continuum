from datetime import UTC

from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStampedModel

from .constants import STEAM_HEADER_IMAGE_BASE_URL


class Game(TimeStampedModel):
    game_id = models.CharField(max_length=255, unique=True, verbose_name="app ID")
    name = models.CharField(max_length=255, verbose_name="game name")
    icon_url = models.URLField(blank=True, null=True, verbose_name="icon URL")
    playtime = models.FloatField(default=0.0, verbose_name="playtime (hours)")
    raw_data = models.JSONField(verbose_name="raw steam JSON")

    class Meta:
        ordering = ('-playtime',)
        indexes = (
            models.Index(fields=['playtime']),
            models.Index(fields=['name']),
        )
        verbose_name = "Game"
        verbose_name_plural = "Games"

    def get_absolute_url(self):
        return reverse('games:game-detail', args=[self.pk])

    def get_header_image_url(self):
        return f'{STEAM_HEADER_IMAGE_BASE_URL}{self.game_id}/header.jpg'

    def get_last_played(self):
        last_played_timestamp = self.raw_data.get('rtime_last_played')
        if last_played_timestamp:
            return timezone.datetime.fromtimestamp(
                last_played_timestamp, tz=UTC
            )
        return None

    def __str__(self):
        return f'{self.name} (Playtime: {self.playtime:.1f} hours)'


class GameActivity(TimeStampedModel):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name="Game"
    )
    playtime = models.IntegerField(
        verbose_name="Playtime (minutes)"
    )

    class Meta:
        ordering = ('-created_at',)
        indexes = (
            models.Index(fields=['created_at']),
            models.Index(fields=['game', 'created_at']),
        )
        verbose_name = "game activity"
        verbose_name_plural = "game activities"

    def __str__(self):
        return f"{self.game.name} [{self.created_at.strftime('%Y-%m-%d')}]"
