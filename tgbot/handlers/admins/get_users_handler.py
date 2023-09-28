from aiogram import F, Router, html
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from pymongo import ASCENDING

from tgbot.db.db_api import users, user_categories
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admins.get_users_func import get_user_info
from tgbot.keyboards.inline.users_keyboards import paginate_users, UserCallbackFactory, current_user_keyboard, \
    accept_keyboard

admin_users_router = Router()
admin_users_router.message.filter(AdminFilter(), F.chat.type == "private")


@admin_users_router.message(F.text == 'Пользователи')
async def get_users(message: Message):
    cursor = users.find().sort('role', ASCENDING)
    _users = await cursor.to_list(length=None)
    text, keyboard = await paginate_users(_users)
    await message.answer(text=text,
                         reply_markup=keyboard)


@admin_users_router.callback_query(F.data.contains('users_page:'))
async def change_users_page(call: CallbackQuery):
    data = call.data.split(':')
    page = int(data[1])
    cursor = users.find().sort('role', ASCENDING)
    _users = await cursor.to_list(length=None)
    text, keyboard = await paginate_users(_users, page=page)
    await call.message.edit_text(text=text,
                                 reply_markup=keyboard)


@admin_users_router.callback_query(UserCallbackFactory.filter(F.action == 'choose'))
async def get_user(call: CallbackQuery, callback_data: UserCallbackFactory):
    user_id = callback_data.user_id
    page = callback_data.page

    user = await users.find_one({'_id': user_id})
    text = await get_user_info(user=user)
    await call.message.edit_text(text=text,
                                 reply_markup=current_user_keyboard(user_id=user_id,
                                                                    page=page))


@admin_users_router.callback_query(UserCallbackFactory.filter(F.action == 'delete'))
async def delete_user(call: CallbackQuery, callback_data: UserCallbackFactory):
    user_id = callback_data.user_id
    page = callback_data.page
    await call.message.edit_text(text='Вы уверены, что хотите удалить этого пользователя?',
                                 reply_markup=accept_keyboard(user_id=user_id,
                                                              page=page))


@admin_users_router.callback_query(UserCallbackFactory.filter(F.action == 'accept_delete'))
async def accept_delete_category(call: CallbackQuery, callback_data: UserCallbackFactory):
    user_id = callback_data.user_id

    await users.delete_one({'_id': user_id})
    await user_categories.delete_many({'user_id': user_id})

    await call.answer('Пользователь успешно удален!')
    await get_users(call.message)
    await call.message.delete()


@admin_users_router.callback_query(UserCallbackFactory.filter(F.action == 'change_description'))
async def change_description(call: CallbackQuery, callback_data: UserCallbackFactory, state: FSMContext):
    user_id = callback_data.user_id
    page = callback_data.page
    await state.set_state('waiting_description')
    await state.update_data(user_id=user_id,
                            page=page)
    await call.message.edit_text('Отправьте описание пользователя')


@admin_users_router.message(StateFilter('waiting_description'), F.text)
async def waiting_description(message: Message, state: FSMContext):
    description = message.text.strip()

    if len(description) < 1:
        await message.answer(html.bold('Описание должно содержать хотя бы 1 символ'))
        return
    if len(description) > 100:
        await message.answer(html.bold('Описание не должно превышать 100 символов.'))
        return

    data = await state.get_data()
    user_id = data.get('user_id')
    page = data.get('page')

    await users.update_one(filter={'_id': user_id},
                           update={'$set': {'description': description}})

    user = await users.find_one({'_id': user_id})
    text = await get_user_info(user=user)
    await message.answer(text=text,
                         reply_markup=current_user_keyboard(user_id=user_id,
                                                            page=page))
    await state.clear()