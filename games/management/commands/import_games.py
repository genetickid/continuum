import os

from db_services import GameDBService
from django.core.management.base import BaseCommand
from services import SteamGameService


class Command(BaseCommand):
    help = 'Import your game library from Steam API and save it to the database.'

    def handle(self, *args, **kwargs):
        api_key = os.getenv('STEAM_API_KEY')
        steam_id = os.getenv('STEAM_ID')

        if not api_key or not steam_id:
            self.stdout.write(
                self.style.ERROR('STEAM_API_KEY and STEAM_ID env variables'
                                 ' must be set to import Steam games.')
            )
            return

        steam_service = SteamGameService()
        owned_games = steam_service.get_user_games(
            user_id=steam_id,
            api_key=api_key
        )

        if not owned_games:
            self.stdout.write(
                self.style.WARNING('No games found for this Steam ID.')
            )
            return

        self.stdout.write(f'Found {len(owned_games)} games. Starting import...')

        success_count, error_count = GameDBService.save_games(owned_games)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {success_count} games.')
        )

        if error_count > 0:
            self.stdout.write(
                self.style.WARNING(f'Failed to import {error_count} games.')
            )
