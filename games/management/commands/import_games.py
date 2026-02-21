import os
import time
from http import HTTPStatus

import requests
from django.core.management.base import BaseCommand

from games.models import Game, GameActivity

STEAM_API_URL = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
STEAM_STORE_URL = 'http://store.steampowered.com/api/appdetails'
STEAM_IMAGE_BASE_URL = 'http://media.steampowered.com/steamcommunity/public/images/apps/'


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

        owned_games = self._get_owned_games(api_key, steam_id)

        if not owned_games:
            self.stdout.write(
                self.style.WARNING('No games found for this Steam ID.')
            )
            return

        self.stdout.write(f'Found {len(owned_games)} games. Starting import...')

        success_count = 0
        error_count = 0

        for game_data in owned_games:
            try:
                self._process_single_game(game_data)
                success_count += 1
            except Exception as e:
                app_id = game_data.get('appid')
                self.stdout.write(
                    self.style.ERROR(f'Failed to process game ID {app_id}: {e}')
                )
                error_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully imported {success_count} games.')
        )
        self.stdout.write(
            self.style.WARNING(f'Failed to import {error_count} games.')
        )

    def _get_owned_games(self, api_key, steam_id):
        params = {
            'key': api_key,
            'steamid': steam_id,
            'include_appinfo': True,
            'include_played_free_games': True,
        }

        try:
            response = requests.get(
                STEAM_API_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return (
                response.json()
                .get('response', {})
                .get('games', [])
            )
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'API Request failed: {e}'))
            return []

    def _get_store_details(self, app_id):
        try:
            time.sleep(1.2)
            response = requests.get(
                STEAM_STORE_URL,
                params={'appids': app_id},
                timeout=10
            )
            if response.status_code == HTTPStatus.OK:
                return (
                    response.json()
                    .get(str(app_id), {})
                    .get('data', {})
                )
        except requests.RequestException as e:
            self.stdout.write(
                self.style.WARNING(f'Could not fetch store details for {app_id}: {e}')
            )
        return {}

    def _process_single_game(self, game_data):
        app_id = game_data.get('appid')
        name = game_data.get('name', 'Unknown Game')
        playtime = game_data.get('playtime_forever', 0) / 60

        store_data = {}
        if playtime > 0:
            store_data = self._get_store_details(app_id)

        full_data = {**game_data, **store_data}
        icon_hash = game_data.get('img_icon_url')
        icon_url = f'{STEAM_IMAGE_BASE_URL}{app_id}/{icon_hash}.jpg' if icon_hash else ''

        game_obj, created = Game.objects.update_or_create(
            game_id=app_id,
            defaults={
                'name': name,
                'playtime': playtime,
                'icon_url': icon_url,
                'raw_data': full_data,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'New game added: {name}'))

        GameActivity.objects.create(game=game_obj, playtime=playtime)
