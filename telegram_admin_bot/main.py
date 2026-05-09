from __future__ import annotations

import asyncio
import logging
import os
import time
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand, BotCommandScopeChat
from aiogram.exceptions import TelegramConflictError

from telegram_admin_bot.config import load_config

from src.repositories.storage import configure_database_path, init_storage

from .handlers import admin as admin_handlers


logger = logging.getLogger(__name__)
HEARTBEAT_PATH = Path(os.getenv('ADMIN_BOT_HEARTBEAT_PATH', '/tmp/appslides_admin_bot.heartbeat'))


def _touch_heartbeat() -> None:
    try:
        HEARTBEAT_PATH.write_text(str(int(time.time())), encoding='utf-8')
    except OSError:
        logger.exception('Failed to write admin bot heartbeat')


async def _set_commands(bot: Bot, admin_ids: list[int]) -> None:
    commands = [
        BotCommand(command='botstats', description='Общая статистика'),
        BotCommand(command='adstats', description='Статистика по метке'),
        BotCommand(command='adstats_all', description='Статистика по всем меткам'),
        BotCommand(command='adtag', description='Создать рекламную метку'),
        BotCommand(command='tag', description='Создать рекламную метку (alias)'),
        BotCommand(command='sub_on', description='Начислить генерации'),
        BotCommand(command='sub_off', description='Обнулить генерации'),
        BotCommand(command='sub_check', description='Проверить баланс'),
        BotCommand(command='sub_cancel', description='Отключить подписку'),
        BotCommand(command='genpromo', description='Создать промокод'),
        BotCommand(command='admin_add', description='Добавить админа'),
        BotCommand(command='admin_del', description='Удалить админа'),
        BotCommand(command='admin_list', description='Список админов'),
        BotCommand(command='templates', description='Показать шаблоны'),
        BotCommand(command='template_set', description='Заменить шаблон'),
    ]
    await bot.set_my_commands(commands)
    for admin_id in admin_ids:
        try:
            await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=admin_id))
        except Exception:
            continue


async def _poll_updates(bot: Bot, dp: Dispatcher) -> None:
    offset: int | None = None
    retry_delay = 1.0

    await bot.delete_webhook(drop_pending_updates=False)
    _touch_heartbeat()
    logger.info('Admin bot polling started')

    while True:
        try:
            updates = await bot.get_updates(
                offset=offset,
                timeout=20,
                allowed_updates=['message'],
                request_timeout=35,
            )
            _touch_heartbeat()
            retry_delay = 1.0

            for update in updates:
                offset = update.update_id + 1
                try:
                    await dp.feed_update(bot, update)
                except Exception:
                    logger.exception('Failed to handle admin bot update %s', update.update_id)
        except TelegramConflictError:
            logger.exception('Admin bot polling conflict: another getUpdates consumer is active')
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception('Admin bot polling failed; retrying in %.1f seconds', retry_delay)
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 1.5, 20.0)


async def main() -> None:
    logging.basicConfig(
        level=os.getenv('ADMIN_BOT_LOG_LEVEL', os.getenv('LOG_LEVEL', 'INFO')).upper(),
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    )

    config = load_config()
    if not config.bot_token:
        raise RuntimeError('ADMIN_BOT_TOKEN is not set')

    configure_database_path(config.database_path)
    init_storage(config.database_path)

    session = AiohttpSession(timeout=45)
    bot = Bot(token=config.bot_token, session=session)
    dp = Dispatcher()
    dp.include_router(admin_handlers.router)

    try:
        await _set_commands(bot, config.admin_ids)
        await _poll_updates(bot, dp)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
