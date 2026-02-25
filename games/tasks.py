import logging

from celery import shared_task

from core.models import BackgroundTask

from .db_services import GameDBService
from .services import SteamGameService

logger = logging.getLogger(__name__)


@shared_task
def import_steam_games(steam_id: str, api_key: str, db_task_id: int):
    logger.info(f'Starting Steam games import for user {steam_id}...')

    try:
        steam_service = SteamGameService()
        owned_games = steam_service.get_user_games(
            user_id=steam_id,
            api_key=api_key
        )

        if not owned_games:
            BackgroundTask.change_status(
                db_task_id, BackgroundTask.Status.FAILED
            )
            logger.warning('No games found for this Steam ID.')
            return

        success_count, error_count = GameDBService.save_games(owned_games)
        BackgroundTask.change_status(
            db_task_id, BackgroundTask.Status.SUCCESS
        )
        logger.info(f'Import finished. Successfully imported: {success_count}, Errors: {error_count}.')

    except Exception as e:
        BackgroundTask.change_status(
            db_task_id, BackgroundTask.Status.FAILED
        )
        logger.error(f'Error during import: {e}')
        raise e
