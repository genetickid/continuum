from datetime import datetime

from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel


class Game(TimeStampedModel):
    game_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    icon_url = models.URLField(blank=True, null=True)
    playtime = models.IntegerField(default=0)
    raw_data = models.JSONField()

    class Meta:
        ordering = ['-playtime']

    def get_absolute_url(self):
        return reverse('games:game-detail', args=[self.pk])

    def get_header_image_url(self):
        return f'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{self.game_id}/header.jpg'

    def get_last_played(self):
        last_played_timestamp = self.raw_data.get('rtime_last_played')
        if last_played_timestamp:
            return datetime.fromtimestamp(last_played_timestamp)
        return None

    def __str__(self):
        return f'{self.name} - {self.playtime} hours played'
