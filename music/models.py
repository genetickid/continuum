from django.db import models

from core.models import TimeStampedModel


class MusicTrack(TimeStampedModel):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album = models.CharField(max_length=255, blank=True, null=True)
    spotify_id = models.CharField(max_length=255, unique=True, db_index=True)
    duration = models.IntegerField()
    raw_data = models.JSONField()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.artist} - {self.name}'
