import asyncio
import re

from aiogram import Router, F, html, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bson import ObjectId
from pymongo import DESCENDING

from tgbot.db.db_api import categories, user_categories, users
from tgbot.db.service import get_instruction
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.admins.categories_func import get_category_info
from tgbot.keyboards.default.reply import admin_keyboard
from tgbot.keyboards.inline.categories_keyboards import paginate_categories, categories_keyboard, \
    current_category_keyboard, CategoryCallbackFactory, accept_keyboard, accept_getting_message
from tgbot.types import Album

admin_router = Router()
admin_router.message.filter(AdminFilter(), F.chat.type == "private")


@admin_router.message(Command(commands='start'))
async def admin_start(message: Message, state: FSMContext):
    await state.clear()
    instruction = await get_instruction()
    await message.answer(html.quote(instruction),
                         reply_markup=admin_keyboard)


@admin_router.message(F.text == 'Категории')
async def get_categories_menu(message: Message):
    await message.answer('Выберите действие',
                         reply_markup=categories_keyboard)


# Ветка "Список категорий"
@admin_router.callback_query(F.data == 'get_categories')
async def get_categories(call: CallbackQuery):
    cursor = categories.find().sort('date', DESCENDING)
    categories_list = await cursor.to_list(length=None)
    if not categories_list:
        await call.answer('Список категорий пуст. Для начала добавьте хотя бы 1 категорию.')
        return

    text, keyboard = await paginate_categories(categories_list)
    await call.message.edit_text('<b>Список категорий:</b>\n'
                                 f'{text}',
                                 reply_markup=keyboard)


@admin_router.callback_query(F.data.contains('categories_page:'))
async def change_category_page(call: CallbackQuery):
    data = call.data.split(':')
    page = int(data[1])
    cursor = categories.find().sort('date', DESCENDING)
    categories_list = await cursor.to_list(length=None)
    text, keyboard = await paginate_categories(categories_list, page=page)

    await call.message.edit_text('<b>Категории:</b>\n'
                                 f'{text}',
                                 reply_markup=keyboard)


@admin_router.callback_query(CategoryCallbackFactory.filter(F.action == 'choose'))
async def get_category(call: CallbackQuery, callback_data: CategoryCallbackFactory):
    _id = ObjectId(callback_data.category_id)
    page = callback_data.page

    category = await categories.find_one({'_id': _id})
    text = await get_category_info(category=category, current=True)
    await call.message.edit_text(text=text,
                                 reply_markup=current_category_keyboard(category_id=_id,
                                                                        page=page))


@admin_router.callback_query(CategoryCallbackFactory.filter(F.action == 'add_user'))
async def add_user_in_category(call: CallbackQuery, callback_data: CategoryCallbackFactory, state: FSMContext):
    _id = ObjectId(callback_data.category_id)
    page = callback_data.page

    await call.message.answer('<b>Отправьте ссылку или ID пользователя</b>')
    await state.set_state('waiting_user_id')
    await state.update_data(category_id=_id,
                            page=page)


@admin_router.message(StateFilter('waiting_user_id'), F.text)
async def waiting_user_id(message: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data.get('category_id')

    text = message.text.strip()
    if text.isdigit():
        user_id = int(text)
        user = await users.find_one({'_id': user_id})
        if not user:
            await message.answer('<b>Пользователь не найден!</b>')
            return
    else:
        username = re.sub(r'@|https:|t\.me|/', '', text)
        user = await users.find_one({'username': {'$regex': f'^{username}$', '$options': 'i'}})
        if not user:
            await message.answer('<b>Пользователь не найден!</b>')
            return
    user_id = user['_id']

    user_in_category = await user_categories.find_one({'user_id': user_id,
                                                       'category_id': category_id})
    if user_in_category:
        await message.answer('<b>Пользователь уже принадлежит этой категории</b>')
        return

    await user_categories.insert_one({'user_id': user_id,
                                      'category_id': category_id})
    await message.answer('<b>Пользователь успешно добавлен в категорию</b>')
    await state.clear()


@admin_router.callback_query(CategoryCallbackFactory.filter(F.action == 'rename'))
async def rename_category(call: CallbackQuery, callback_data: CategoryCallbackFactory, state: FSMContext):
    _id = ObjectId(callback_data.category_id)
    page = callback_data.page

    await call.answer('Введите новое название')
    await state.set_state('waiting_new_category_name')
    await state.update_data(_id=_id,
                            page=page)


@admin_router.message(StateFilter('waiting_new_category_name'), F.text)
async def waiting_new_category_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) > 64:
        await message.answer('Длина названия не может превышать 64 символов!')
        return

    category = await categories.find_one({'name': name})
    if category:
        await message.answer('Категория с таким названием уже существует!')
        return

    data = await state.get_data()
    _id = data.get('_id')
    await categories.update_one({'_id': _id},
                                {'$set': {'name': name}})
    await state.clear()
    await message.answer(f'Название изменено на <b>{name}</b>')


@admin_router.callback_query(CategoryCallbackFactory.filter(F.action == 'delete'))
async def delete_category(call: CallbackQuery, callback_data: CategoryCallbackFactory):
    _id = ObjectId(callback_data.category_id)
    page = callback_data.page
    await call.message.edit_text(text='Вы уверены, что хотите удалить эту категорию?',
                                 reply_markup=accept_keyboard(category_id=_id,
                                                              page=page))


@admin_router.callback_query(CategoryCallbackFactory.filter(F.action == 'accept_delete'))
async def accept_delete_category(call: CallbackQuery, callback_data: CategoryCallbackFactory):
    _id = ObjectId(callback_data.category_id)

    await categories.delete_one({'_id': _id})
    await user_categories.delete_many({'category_id': _id})

    await call.answer('Категория успешно удалена!')
    await get_categories(call)
    await call.message.delete()


# Ветка "Создать новую категорию"
@admin_router.callback_query(F.data == 'create_category')
async def create_category(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Отправьте название категории')
    await state.set_state('waiting_category_name')


@admin_router.message(StateFilter('waiting_category_name'), F.text)
async def waiting_category_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    date = message.date

    name = message.text.strip()
    if len(name) > 64:
        await message.answer('Длина названия не может превышать 64 символов!')
        return

    category = await categories.find_one({'name': name})
    if category:
        await message.answer('Категория с таким названием уже существует!')
        return

    new_category = await categories.insert_one({'created_by': user_id,
                                                'name': name,
                                                'date': date})
    _id = new_category.inserted_id
    category = await categories.find_one({'_id': _id})
    text = await get_category_info(category)

    await message.answer(f'Категория <b>{name}</b> успешно создана!')
    await message.answer(text=text,
                         reply_markup=current_category_keyboard(category_id=_id,
                                                                page=1))
    await state.clear()


@admin_router.callback_query(CategoryCallbackFactory.filter(F.action == 'send_message'))
async def send_message(call: CallbackQuery, callback_data: CategoryCallbackFactory, state: FSMContext):
    _id = ObjectId(callback_data.category_id)
    await state.set_state('waiting_category_message')
    await state.update_data(category_id=_id)
    await call.answer('Отправьте сообщение')


@admin_router.message(StateFilter('waiting_category_message'))
async def waiting_category_message(message: Message, bot: Bot, state: FSMContext, album: Album = None):
    data = await state.get_data()
    category_id = data.get('category_id')

    cursor = user_categories.find({'category_id': category_id})
    users_in_category = await cursor.to_list(length=None)
    await message.answer(text='<b>Подтвердите получение</b>',
                         reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                             message_id=message.message_id))
    for user in users_in_category:
        print(user)
        await asyncio.sleep(0.1)

        user_id = user['user_id']
        if album:
            await album.copy_to(chat_id=user_id)
            await bot.send_message(chat_id=user_id,
                                   text='<b>Подтвердите получение</b>',
                                   reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                                       message_id=message.message_id))
            continue
        else:
            await message.copy_to(chat_id=user_id,
                                  reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                                      message_id=message.message_id))
