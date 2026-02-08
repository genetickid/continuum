import os
import time
from http import HTTPStatus

import requests
from django.core.management.base import BaseCommand

from games.models import Game


class Command(BaseCommand):
    help = 'Import your game library from Steam API and save it to the database.'

    def handle(self, *args, **kwargs):
        api_key = os.getenv('STEAM_API_KEY')
        steam_id = os.getenv('STEAM_ID')

        if not api_key or not steam_id:
            self.stdout.write(
                self.style.ERROR('STEAM_API_KEY and STEAM_ID environment variables must be set to import games from Steam.')
            )
            return

        owned_games = self.get_owned_games(api_key, steam_id)

        if not owned_games:
            self.stdout.write(self.style.WARNING('No games found for this Steam ID.'))
            return

        for game_data in owned_games:
            try:
                self.process_single_game(game_data)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to process game ID {game_data.get('appid')}: {e}"))

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(owned_games)} games.'))

    def get_owned_games(self, api_key, steam_id):
        url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
        params = {
            'key': api_key,
            'steamid': steam_id,
            'include_appinfo': True,
            'include_played_free_games': True,
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('response', {}).get('games', [])
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'API Request failed: {e}'))
            return []

    def get_additional_info(self, app_id):
        url = 'http://store.steampowered.com/api/appdetails'
        params = {'appids': app_id}

        try:
            time.sleep(1.2)
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == HTTPStatus.OK:
                data = response.json()
                game_response = data.get(str(app_id), {})

                return game_response.get('data', {})
        except Exception:
            pass

        return {}

    def process_single_game(self, game_data):
        app_id = game_data['appid']
        playtime = game_data.get('playtime_forever', 0) / 60

        store_data = {}
        if playtime > 0:
            store_data = self.get_additional_info(app_id)

        full_data = {**game_data, **store_data}

        icon_hash = game_data.get('img_icon_url')
        icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{app_id}/{icon_hash}.jpg" if icon_hash else ""

        game_obj, created = Game.objects.update_or_create(
            game_id=app_id,
            defaults={
                'name': game_data['name'],
                'playtime': playtime,
                'icon_url': icon_url,
                'raw_data': full_data,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created: {game_obj.name}'))
