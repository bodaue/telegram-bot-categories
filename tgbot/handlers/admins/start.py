from aiogram import Router, F, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.db.db_api import users
from tgbot.db.service import get_instruction
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admins.categories_handlers.categories_handler import categories_router
from tgbot.handlers.admins.get_users_handler import admin_users_router
from tgbot.handlers.admins.settings_handler import admin_settings_router
from tgbot.keyboards.default.reply import admin_keyboard

admin_router = Router()
admin_router.message.filter(AdminFilter(), F.chat.type == "private")
admin_router.callback_query.filter(AdminFilter(), F.message.chat.type == "private")

admin_router.include_routers(admin_users_router,
                             admin_settings_router,
                             categories_router)


@admin_router.message(Command(commands='start'))
async def admin_start(message: Message, state: FSMContext):
    users_list = users.find()
    async for u in users_list:
        print(u)
    await state.clear()
    instruction = await get_instruction()
    await message.answer(html.quote(instruction),
                         reply_markup=admin_keyboard)
