import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from tgbot.db.service import create_default_passwords
from tgbot.handlers.admins.categories_handler import admin_categories_router
from tgbot.handlers.admins.get_users_handler import admin_users_router
from tgbot.handlers.admins.settings_handler import admin_settings_router
from tgbot.handlers.admins.start import admin_router
from tgbot.handlers.users.start import user_router
from tgbot.middlewares.album import AlbumMiddleware
from tgbot.middlewares.authorization import AuthorizationMiddleware
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.middlewares.update_user_data import UpdateUserDataMiddleware
from tgbot.misc.mongostorage import MongoStorage
from tgbot.misc.set_bot_commands import set_default_commands
from tgbot.services import broadcaster

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот запущен!")


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(AuthorizationMiddleware())
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))
    dp.message.outer_middleware(UpdateUserDataMiddleware())

    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.message.middleware(AlbumMiddleware())


def register_logger():
    logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-6s [%(asctime)s]  %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S',
                        level=log_level)
    logger.info("Starting bot")


async def main():
    from tgbot.config import config

    await create_default_passwords(admin_password=config.tg_bot.default_admin_password,
                                   user_password=config.tg_bot.default_user_password)

    register_logger()

    if config.tg_bot.use_mongo_storage:
        storage = MongoStorage(uri='mongodb://127.0.0.1:27017/',
                               database='FSM_states',
                               collection_states='states')
    else:
        storage = MemoryStorage()

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)

    for router in [
        admin_router,
        admin_users_router,
        admin_settings_router,
        admin_categories_router,
        user_router,
    ]:
        dp.include_router(router)

    register_global_middlewares(dp, config)

    await set_default_commands(bot)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Stopping bot")
