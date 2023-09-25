from aiogram import F, Router
from aiogram.types import Message
from pymongo import ASCENDING

from tgbot.db.db_api import users
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline.users_keyboards import paginate_users

admin_users_router = Router()
admin_users_router.message.filter(AdminFilter(), F.chat.type == "private")


@admin_users_router.message(F.text == 'Пользователи')
async def get_users(message: Message):
    cursor = users.find().sort('role', ASCENDING)
    _users = await cursor.to_list(length=None)
    text, keyboard = await paginate_users(_users)
    await message.answer(text=text,
                         reply_markup=keyboard)
