import logging

from .constants import STEAM_IMAGE_BASE_URL
from .models import Game, GameActivity

logger = logging.getLogger(__name__)


class GameDBService:
    @staticmethod
    def save_games(games: list[dict]) -> tuple[int, int]:
        success_count = 0
        error_count = 0

        for game_data in games:
            app_id = game_data.get('appid')
            name = game_data.get('name', 'Unknown Game')
            playtime = game_data.get('playtime_forever', 0) / 60

            try:
                icon_hash = game_data.get('img_icon_url')
                icon_url = f'{STEAM_IMAGE_BASE_URL}{app_id}/{icon_hash}.jpg' if icon_hash else ''

                game_obj, created = Game.objects.update_or_create(
                    game_id=app_id,
                    defaults={
                        'name': name,
                        'playtime': playtime,
                        'icon_url': icon_url,
                        'raw_data': game_data,
                    }
                )

                GameActivity.objects.create(game=game_obj, playtime=playtime)

                if created:
                    success_count += 1
                    logger.info(f'Added new game: {name}')

            except Exception as e:
                error_count += 1
                logger.error(f'Failed to save game: {name}, error: {e}')

        return success_count, error_count
