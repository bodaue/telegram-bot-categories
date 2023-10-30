import asyncio
import re
from asyncio import sleep
from contextlib import suppress
from pathlib import Path

from aiogram import F, Bot, Router
from aiogram.enums import InputMediaType
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from bson import ObjectId
from pymongo import DESCENDING

from tgbot.db.db_api import categories, user_categories, dialogs
from tgbot.db.service import get_admins
from tgbot.filters.cords import HasCords
from tgbot.filters.dialog import IsDialog
from tgbot.filters.file_type import FileExtension
from tgbot.handlers.admins.categories_handlers.categories_func import get_valid_categories
from tgbot.handlers.admins.categories_handlers.list_categories import list_categories_router
from tgbot.keyboards.inline.categories_keyboards import paginate_categories, CategoryCallbackFactory, \
    accept_getting_message, type_send_message
from tgbot.services.point import Point
from tgbot.services.zipfile_utils import unpack_zipfile
from tgbot.types import Album
from tgbot.types.mimetype import MimeType

ZIP_PATH = '/root/bot_categories/tgbot/downloaded_files/zip/'
FOLDER_PATH = '/root/bot_categories/tgbot/downloaded_files/folders/'

# ZIP_PATH = 'tgbot/downloaded_files/zip/'
# FOLDER_PATH = 'tgbot/downloaded_files/folders/'
send_message_category_router = Router()


@list_categories_router.callback_query(CategoryCallbackFactory.filter(F.action == 'send_message'))
async def choose_type_send_message(call: CallbackQuery, callback_data: CategoryCallbackFactory):
    await call.message.answer('<b>Выберите один из вариантов:</b>\n'
                              'Если выбрать "С оповещением", тогда админы получат оповещение о том, что Вы отправили'
                              ' сообщение в эту категорию.',
                              reply_markup=type_send_message(category_id=callback_data.category_id,
                                                             page=callback_data.page))


@list_categories_router.callback_query(CategoryCallbackFactory.filter(F.action.in_(('send_message_with_notify',
                                                                                    'send_message_without_notify'))))
async def send_message(call: CallbackQuery, callback_data: CategoryCallbackFactory, state: FSMContext):
    _id = ObjectId(callback_data.category_id)
    await state.set_state('waiting_category_message')
    if callback_data.action == 'send_message_with_notify':
        notify = True
    else:
        notify = False
    await state.update_data(category_id=_id,
                            notify=notify)
    await call.message.edit_text('Отправьте сообщение')


@list_categories_router.message(StateFilter('waiting_category_message'))
async def waiting_category_message(message: Message, bot: Bot, state: FSMContext, album: Album = None):
    data = await state.get_data()
    category_id = data.get('category_id')
    notify = data.get('notify')

    category = await categories.find_one({'_id': category_id})
    category_name = category['name']

    cursor = user_categories.find({'category_id': category_id})
    users_in_category = await cursor.to_list(length=None)

    await state.clear()

    if notify:
        admins = await get_admins()
        for admin in admins:
            with suppress(TelegramAPIError):
                await bot.send_message(chat_id=admin['_id'],
                                       text=f'<b>Администратор {message.from_user.mention_html()} отправил следующее '
                                            f'сообщение в категорию "{category_name}</b>"')
                if album:
                    await album.copy_to(admin['_id'])
                else:
                    await message.copy_to(admin['_id'])
    for user in users_in_category:
        await asyncio.sleep(0.1)
        user_id = user['user_id']
        with suppress(TelegramAPIError):
            if album:
                await album.copy_to(chat_id=user_id)
                m = await bot.send_message(chat_id=user_id,
                                           text='<b>Подтвердите получение</b>',
                                           reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                                               message_id=message.message_id))

            else:
                m = await message.copy_to(chat_id=user_id,
                                          reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                                              message_id=message.message_id))
            await dialogs.insert_one({'admin_id': message.from_user.id,
                                      'admin_message_id': message.message_id,
                                      'user_id': user_id,
                                      'user_message_id': m.message_id})
    await message.reply('Сообщение было отправлено')


@send_message_category_router.message(F.reply_to_message, IsDialog())
async def reply_to_message(message: Message, dialog: dict):
    admin_id = message.from_user.id

    user_id = dialog['user_id']
    user_message_id = dialog['user_message_id']

    await message.copy_to(chat_id=user_id,
                          reply_to_message_id=user_message_id)
    await dialogs.update_one(filter={'admin_id': admin_id,
                                     'admin_message_id': message.reply_to_message.message_id,
                                     'user_id': dialog['user_id']},
                             update={'$set': {'admin_message_id': message.message_id}})
    await message.answer('Сообщение было отправлено')


@send_message_category_router.message(FileExtension(MimeType.ZIP.value))
async def send_zip_message(message: Message, bot: Bot):
    document = message.document

    cursor = categories.find().sort('date', DESCENDING)
    categories_list = await cursor.to_list(length=None)

    for category in categories_list:
        name = category['name']
        if re.search(fr'^{name}', document.file_name, re.IGNORECASE):
            break
    else:
        await message.answer('<b>Название архива не начинается с названия категории</b>')
        return

    await bot.download(file=document.file_id,
                       destination=Path(ZIP_PATH + document.file_name))
    files = unpack_zipfile(ZIP_PATH + document.file_name,
                           FOLDER_PATH + name)
    if not files:
        await message.answer('<b>Архив не содержит файлов</b>')
        return

    send_photos = True
    for file in files:
        if not re.search(fr'^{name}', file, re.IGNORECASE):
            send_photos = False

    cursor = user_categories.find({'category_id': category['_id']})
    users_in_category = await cursor.to_list(length=None)
    for user in users_in_category:
        with suppress(TelegramAPIError):
            await asyncio.sleep(0.1)
            user_id = user['user_id']
            if not send_photos:
                await message.copy_to(chat_id=user_id)
            else:
                media_group = MediaGroupBuilder(caption=message.caption if message.caption else '')
                for index, file in enumerate(files):
                    sent = False
                    photo = FSInputFile(path=f'{FOLDER_PATH}{name}/{file}')
                    media_group.add(type=InputMediaType.PHOTO,
                                    media=photo)
                    if (index != 0) and (index % 9 == 0):
                        await bot.send_media_group(chat_id=user_id,
                                                   media=media_group.build())
                        sent = True
                        media_group = MediaGroupBuilder()

                if not sent:
                    await bot.send_media_group(chat_id=user_id,
                                               media=media_group.build())
    await message.answer(f'<b>Архив был отправлен в категорию {name}</b>')


forwarded_messages = {}


@send_message_category_router.message(HasCords())
async def cords_in_text(message: Message, state: FSMContext, points: list[Point]):
    point = None
    valid_categories = list()

    for point in points:
        valid_categories = await get_valid_categories(point)
        if valid_categories:
            break

    if not valid_categories:
        await message.answer(
            f'<b>Координаты {point} обнаружены в тексте, но подходящая категория не найдена</b>')
        return
    text, keyboard = await paginate_categories(valid_categories)
    await message.answer(f'<b>Координаты {point} были обнаружены в следующих категориях:</b>\n\n'
                         f'{text}',
                         reply_markup=keyboard)

    await state.set_state('cords_waiting_category')
    await state.update_data(point=point,
                            message=message)


@list_categories_router.callback_query(F.data.contains('categories_page:'),
                                       StateFilter('cords_waiting_category'))
async def cords_change_category_page(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    point: Point = state_data.get('point')

    data = call.data.split(':')
    page = int(data[1])
    valid_categories = await get_valid_categories(point)
    text, keyboard = await paginate_categories(valid_categories, page=page)

    await call.message.edit_text(f'<b>Координаты {point} были обнаружены в следующих категориях:</b>\n\n'
                                 f'{text}',
                                 reply_markup=keyboard)


@send_message_category_router.callback_query(CategoryCallbackFactory.filter(F.action == 'choose'),
                                             StateFilter('cords_waiting_category'))
async def cords_get_category_to_send_message(call: CallbackQuery,
                                             state: FSMContext,
                                             callback_data: CategoryCallbackFactory):
    _id = ObjectId(callback_data.category_id)

    data = await state.get_data()
    message: Message = data.get('message')

    cursor = user_categories.find({'category_id': _id})
    users_in_category = await cursor.to_list(length=None)

    for user in users_in_category:
        await asyncio.sleep(0.1)
        user_id = user['user_id']
        with suppress(TelegramAPIError):
            m = await message.copy_to(chat_id=user_id,
                                      reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                                          message_id=message.message_id))
            await dialogs.insert_one({'admin_id': message.from_user.id,
                                      'admin_message_id': message.message_id,
                                      'user_id': user_id,
                                      'user_message_id': m.message_id})
    await call.message.edit_text('Сообщение было отправлено')
    await state.clear()


@send_message_category_router.message(F.forward_date)
async def forward_any_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in forwarded_messages:
        forwarded_messages[user_id].append(message)
        return

    forwarded_messages[user_id] = [message]
    await sleep(3)

    cursor = categories.find().sort('date', DESCENDING)
    categories_list = await cursor.to_list(length=None)
    if not categories_list:
        await message.answer('Список категорий пуст. Для начала добавьте хотя бы 1 категорию.')
        return

    text, keyboard = await paginate_categories(categories_list)
    await message.answer(text='<b>Список категорий:</b>\n'
                              f'{text}',
                         reply_markup=keyboard)

    forwarded_messages[user_id].sort(key=lambda x: x.forward_date)
    await state.set_state('waiting_choice_category_forward')
    await state.update_data(forwarded_messages=forwarded_messages[user_id])

    del forwarded_messages[user_id]


@send_message_category_router.callback_query(CategoryCallbackFactory.filter(F.action == 'choose'),
                                             StateFilter('waiting_choice_category_forward'))
async def get_category_to_forward_message(call: CallbackQuery, state: FSMContext,
                                          callback_data: CategoryCallbackFactory):
    _id = ObjectId(callback_data.category_id)

    data = await state.get_data()
    messages = data.get('forwarded_messages')

    cursor = user_categories.find({'category_id': _id})
    users_in_category = await cursor.to_list(length=None)

    for user in users_in_category:
        await asyncio.sleep(0.1)
        user_id = user['user_id']
        for msg in messages:
            with suppress(TelegramAPIError):
                await msg.forward(chat_id=user_id)
        # m = await bot.send_message(chat_id=user_id,
        #                            text='<b>Подтвердите получение</b>',
        #                            reply_markup=accept_getting_message(admin_id=message.from_user.id,
        #                                                                message_id=message.message_id))

        # await dialogs.insert_one({'admin_id': message.from_user.id,
        #                           'admin_message_id': message.message_id,
        #                           'user_id': user_id,
        #                           'user_message_id': m.message_id})
    await call.message.edit_text('Сообщение было отправлено')
    await state.clear()


@send_message_category_router.message()
async def send_any_message(message: Message, state: FSMContext, album: Album = None):
    cursor = categories.find().sort('date', DESCENDING)
    categories_list = await cursor.to_list(length=None)
    if not categories_list:
        await message.answer('Список категорий пуст. Для начала добавьте хотя бы 1 категорию.')
        return

    text, keyboard = await paginate_categories(categories_list)
    await message.answer(text='<b>Список категорий:</b>\n'
                              f'{text}',
                         reply_markup=keyboard)

    await state.set_state('waiting_choice_category_send')
    await state.update_data(message=message,
                            album=album)


@send_message_category_router.callback_query(CategoryCallbackFactory.filter(F.action == 'choose'),
                                             StateFilter('waiting_choice_category_send'))
async def get_category_to_send_message(call: CallbackQuery, bot: Bot, state: FSMContext,
                                       callback_data: CategoryCallbackFactory):
    _id = ObjectId(callback_data.category_id)

    data = await state.get_data()
    message = data.get('message')
    album = data.get('album')

    cursor = user_categories.find({'category_id': _id})
    users_in_category = await cursor.to_list(length=None)

    for user in users_in_category:
        await asyncio.sleep(0.1)
        user_id = user['user_id']
        with suppress(TelegramAPIError):
            if album:
                await album.copy_to(chat_id=user_id)
                m = await bot.send_message(chat_id=user_id,
                                           text='<b>Подтвердите получение</b>',
                                           reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                                               message_id=message.message_id))

            else:
                m = await message.copy_to(chat_id=user_id,
                                          reply_markup=accept_getting_message(admin_id=message.from_user.id,
                                                                              message_id=message.message_id))
            await dialogs.insert_one({'admin_id': message.from_user.id,
                                      'admin_message_id': message.message_id,
                                      'user_id': user_id,
                                      'user_message_id': m.message_id})
    await call.message.edit_text('Сообщение было отправлено')
    await state.clear()
