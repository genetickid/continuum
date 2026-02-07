import os

import requests
from django.core.management.base import BaseCommand

from games.models import Game


class Command(BaseCommand):
    help = 'Import games library using Steam API'

    def handle(self, *args, **kwargs):
        api_key = os.getenv('STEAM_API_KEY')
        steam_id = os.getenv('STEAM_ID')

        if not api_key or not steam_id:
            self.stdout.write(
                self.style.ERROR(
                    'STEAM_API_KEY and STEAM_ID environment variables '
                    'must be set to import games from Steam.'
                )
            )
            return

        url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
        params = {
            'key': api_key,
            'steamid': steam_id,
            'include_appinfo': True,
            'include_played_free_games': True,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            games = data.get('response', {}).get('games', [])

            if not games:
                self.stdout.write(
                    self.style.WARNING('No games found for this Steam ID.')
                )
                return

            for game in games:
                game, created = Game.objects.update_or_create(
                    game_id=game['appid'],
                    defaults={
                        'name': game['name'],
                        'icon_url': f"http://media.steampowered.com/steamcommunity/public/"
                                    f"images/apps/{game['appid']}/{game.get('img_icon_url')}.jpg",
                        'playtime_minutes': game.get('playtime_forever', 0),
                        'raw_data': game,
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Imported new game: {game.name}')
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing games: {e}')
            )
