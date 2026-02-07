from django.contrib import admin

from .models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'playtime', 'game_id', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-playtime',)
    readonly_fields = ('created_at', 'updated_at')
