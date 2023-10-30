import json
import re

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bson import ObjectId
from pymongo import DESCENDING, ReturnDocument

from tgbot.db.db_api import categories, user_categories, users
from tgbot.filters.file_type import FileExtension
from tgbot.handlers.admins.categories_handlers.categories_func import get_category_info
from tgbot.keyboards.inline.categories_keyboards import paginate_categories, current_category_keyboard, \
    CategoryCallbackFactory, accept_keyboard
from tgbot.types.mimetype import MimeType

list_categories_router = Router()

JSON_PATH = '/root/bot_categories/tgbot/downloaded_files/json/'
# JSON_PATH = 'tgbot/downloaded_files/json'


# Ветка "Список категорий"
@list_categories_router.callback_query(F.data == 'get_categories')
async def get_categories(call: CallbackQuery, state: FSMContext):
    await state.clear()
    cursor = categories.find().sort('date', DESCENDING)
    categories_list = await cursor.to_list(length=None)
    if not categories_list:
        await call.answer('Список категорий пуст. Для начала добавьте хотя бы 1 категорию.')
        return

    text, keyboard = await paginate_categories(categories_list)
    await call.message.edit_text('<b>Список категорий:</b>\n'
                                 f'{text}',
                                 reply_markup=keyboard)


@list_categories_router.callback_query(F.data.contains('categories_page:'),
                                       ~StateFilter('cords_waiting_category'))
async def change_category_page(call: CallbackQuery):
    data = call.data.split(':')
    page = int(data[1])
    cursor = categories.find().sort('date', DESCENDING)
    categories_list = await cursor.to_list(length=None)
    text, keyboard = await paginate_categories(categories_list, page=page)

    await call.message.edit_text('<b>Категории:</b>\n'
                                 f'{text}',
                                 reply_markup=keyboard)


@list_categories_router.callback_query(CategoryCallbackFactory.filter(F.action == 'choose'),
                                       ~StateFilter('waiting_choice_category_send'),
                                       ~StateFilter('waiting_choice_category_forward'),
                                       ~StateFilter('cords_waiting_category'))
async def get_category(call: CallbackQuery, callback_data: CategoryCallbackFactory):
    _id = ObjectId(callback_data.category_id)
    page = callback_data.page

    category = await categories.find_one({'_id': _id})
    text = await get_category_info(category=category, current=True)
    await call.message.edit_text(text=text,
                                 reply_markup=current_category_keyboard(category_id=_id,
                                                                        page=page))


@list_categories_router.callback_query(CategoryCallbackFactory.filter(F.action == 'add_user'))
async def add_user_in_category(call: CallbackQuery, callback_data: CategoryCallbackFactory, state: FSMContext):
    _id = ObjectId(callback_data.category_id)
    page = callback_data.page

    await call.message.answer('<b>Отправьте ссылку или ID пользователя</b>')
    await state.set_state('waiting_user_id')
    await state.update_data(category_id=_id,
                            page=page)


@list_categories_router.message(StateFilter('waiting_user_id'), F.text)
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


@list_categories_router.callback_query(CategoryCallbackFactory.filter(F.action == 'rename'))
async def rename_category(call: CallbackQuery, callback_data: CategoryCallbackFactory, state: FSMContext):
    _id = ObjectId(callback_data.category_id)
    page = callback_data.page

    await call.answer('Введите новое название')
    await state.set_state('waiting_new_category_name')
    await state.update_data(_id=_id,
                            page=page)


@list_categories_router.message(StateFilter('waiting_new_category_name'), F.text)
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


@list_categories_router.callback_query(CategoryCallbackFactory.filter(F.action == 'delete'))
async def delete_category(call: CallbackQuery, callback_data: CategoryCallbackFactory):
    _id = ObjectId(callback_data.category_id)
    page = callback_data.page
    await call.message.edit_text(text='Вы уверены, что хотите удалить эту категорию?',
                                 reply_markup=accept_keyboard(category_id=_id,
                                                              page=page))


@list_categories_router.callback_query(CategoryCallbackFactory.filter(F.action == 'accept_delete'))
async def accept_delete_category(call: CallbackQuery, callback_data: CategoryCallbackFactory):
    _id = ObjectId(callback_data.category_id)

    await categories.delete_one({'_id': _id})
    await user_categories.delete_many({'category_id': _id})

    await call.answer('Категория успешно удалена!')
    await call.message.delete()


@list_categories_router.callback_query(CategoryCallbackFactory.filter(F.action == 'set_area'))
async def set_area(call: CallbackQuery, callback_data: CategoryCallbackFactory, state: FSMContext):
    _id = ObjectId(callback_data.category_id)
    page = callback_data.page
    example_text = ('{cords: [[широта_1, долгота_1], [широта_2, долгота_2],'
                    ' [широта_3, долгота_3], [широта_4, долгота_4], [широта_1, долгота 1]]}')
    await call.message.answer('<b>Отправьте .json файл, имеющий следующую структуру:</b>\n'
                              ''
                              f'<code>{example_text}</code>')

    await state.set_state('waiting_json_coordinates')
    await state.update_data(_id=_id,
                            page=page)


@list_categories_router.message(StateFilter('waiting_json_coordinates'), FileExtension(MimeType.JSON.value))
async def waiting_json_coordinates(message: Message, bot: Bot, state: FSMContext):
    document = message.document
    await bot.download(file=document.file_id,
                       destination=JSON_PATH + document.file_name)
    with open(file=JSON_PATH + document.file_name, mode='r') as json_file:
        data = json.load(json_file)
    print(data)

    cords: list = data.get('cords')
    if not cords:
        await message.answer('<b>Не найдено координат в JSON файле.</b>')
        await state.clear()
        return

    if cords[0] == cords[-1]:
        cords.pop()

    if len(cords) < 3:
        await message.answer('<b>Количество точек должно быть больше или равно 3</b>')
        await state.clear()
        return

    if not all([len(cord) == 2 for cord in cords]):
        await message.answer('<b>Каждая точка должна состоять из двух координат. Перепроверьте данные.</b>')
        await state.clear()
        return

    state_data = await state.get_data()
    category_id = state_data.get('_id')
    category = await categories.find_one_and_update(filter={'_id': category_id},
                                                    update={'$set': {'cords': cords}},
                                                    return_document=ReturnDocument.AFTER)
    print(category)
    name = category['name']
    await message.answer(f'<b>Вы успешно изменили область в категории «{name}»</b>')
