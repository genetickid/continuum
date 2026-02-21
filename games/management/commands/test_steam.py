import os

import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Test Steam API connection'

    def handle(self, *args, **kwargs):
        api_key = os.getenv('STEAM_API_KEY')
        steam_id = os.getenv('STEAM_ID')

        if not api_key or not steam_id:
            self.stdout.write(
                self.style.ERROR(
                    'STEAM_API_KEY and STEAM_ID environment variables '
                    'must be set to test the Steam API connection.'
                )
            )
            return

        url = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
        params = {
            'key': api_key,
            'steamids': steam_id,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            players = data.get('response', {}).get('players', [])

            if not players:
                self.stdout.write(
                    self.style.WARNING('Got no player data for this Steam ID.')
                )
                return

            player = players[0]
            nickname = player.get('personaname')
            self.stdout.write(nickname)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Connection error: {e}')
            )
