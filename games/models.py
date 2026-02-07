from django.db import models

from core.models import TimeStampedModel


class Game(TimeStampedModel):
    game_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    icon_url = models.URLField(blank=True, null=True)
    playtime_minutes = models.IntegerField(default=0)
    raw_data = models.JSONField()

    class Meta:
        ordering = ['-playtime_minutes']

    def __str__(self):
        return f"{self.name} - {self.playtime_minutes // 60} hours played"
