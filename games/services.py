import logging
import time
from abc import ABC, abstractmethod
from http import HTTPStatus

import requests

from .constants import STEAM_API_URL, STEAM_STORE_URL

logger = logging.getLogger(__name__)


class GameServiceInterface(ABC):
    @abstractmethod
    def get_user_games(self, user_id: str, api_key: str) -> list[dict]:
        pass


class SteamGameService(GameServiceInterface):
    def get_user_games(self, user_id: str, api_key: str) -> list[dict]:
        raw_games = self._get_games_base_info(user_id, api_key)

        games = []

        for game_data in raw_games:
            app_id = game_data.get('appid')
            playtime = game_data.get('playtime_forever', 0)

            store_data = {}
            if playtime:
                store_data = self._get_store_details(app_id)

            full_game_data = {**game_data, **store_data}
            games.append(full_game_data)

        return games

    def _get_games_base_info(self, user_id: str, api_key: str) -> list[dict]:
        params = {
            'key': api_key,
            'steamid': user_id,
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
            logger.error(f'Failed to get games for user {user_id}: {e}')
            return []

    def _get_store_details(self, app_id: str) -> dict:
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
            logger.warning(f'Failed to get store details for game {app_id}: {e}')
        return {}
