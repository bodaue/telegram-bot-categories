from aiogram import Router, F
from aiogram.types import Message

from tgbot.handlers.admins.categories_handlers.creating_category import creating_category_router
from tgbot.handlers.admins.categories_handlers.list_categories import list_categories_router
from tgbot.handlers.admins.categories_handlers.send_message_all_categories import send_all_categories_router
from tgbot.handlers.admins.categories_handlers.send_message_category import send_message_category_router
from tgbot.keyboards.inline.categories_keyboards import categories_keyboard

categories_router = Router()
categories_router.include_routers(creating_category_router,
                                  list_categories_router,
                                  send_all_categories_router,
                                  send_message_category_router)


@categories_router.message(F.text == 'Категории')
async def get_categories_menu(message: Message):
    await message.answer('Выберите действие',
                         reply_markup=categories_keyboard)
