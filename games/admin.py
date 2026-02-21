from django.contrib import admin

from .models import Game, GameActivity


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'playtime', 'game_id', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('-playtime',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GameActivity)
class GameActivityAdmin(admin.ModelAdmin):
    list_display = ('game', 'playtime', 'created_at')
    search_fields = ('game__name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    list_filter = ('created_at', 'game',)
    list_select_related = ('game',)
