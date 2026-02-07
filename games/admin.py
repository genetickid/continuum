from django.contrib import admin

from .models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'playtime_minutes', 'game_id', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-playtime_minutes',)
    readonly_fields = ('created_at', 'updated_at')
