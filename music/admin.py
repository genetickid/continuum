from django.contrib import admin
from .models import MusicTrack


@admin.register(MusicTrack)
class MusicTrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'artist', 'album', 'duration', 'created_at')
    search_fields = ('name', 'artist', 'album')
    list_filter = ('created_at', 'updated_at')
