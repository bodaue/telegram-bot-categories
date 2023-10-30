from contextlib import suppress

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.db.db_api import user_categories, dialogs
from tgbot.keyboards.inline.categories_keyboards import accept_getting_message
from tgbot.types import Album

send_all_categories_router = Router()


# Ветка "Отправить сообщение всем категориям"
@send_all_categories_router.callback_query(F.data == 'send_message_all_categories')
async def send_message_all_categories(call: CallbackQuery, state: FSMContext):
    await call.answer('Отправьте сообщение')
    await state.set_state('waiting_message_all_categories')


@send_all_categories_router.message(StateFilter('waiting_message_all_categories'))
async def waiting_message_all_categories(message: Message, state: FSMContext, bot: Bot, album: Album = None):
    await state.clear()
    cursor = user_categories.find()
    users_list = await cursor.to_list(length=None)
    users_list = [user['user_id'] for user in users_list]
    users_list = set(users_list)
    for user in users_list:
        with suppress(TelegramAPIError):
            if album:
                await album.copy_to(chat_id=user)
                m = await bot.send_message(chat_id=user,
                                           text='<b>Подтвердите получение</b>',
                                           reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                                               message_id=message.message_id))

            else:
                m = await message.copy_to(chat_id=user,
                                          reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                                              message_id=message.message_id))
            await dialogs.insert_one({'admin_id': message.from_user.id,
                                      'admin_message_id': message.message_id,
                                      'user_id': user,
                                      'user_message_id': m.message_id})
