import math

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bson import ObjectId

from tgbot.handlers.admins.categories_handlers.categories_func import get_category_info

categories_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Создать новую категорию',
                             callback_data='create_category'),
        InlineKeyboardButton(text='Список категорий',
                             callback_data='get_categories')
    ],
    [
        InlineKeyboardButton(text='Отправить сообщение всем категориям',
                             callback_data='send_message_all_categories')
    ]
])


class CategoryCallbackFactory(CallbackData, prefix="category"):
    action: str
    category_id: str
    page: int = None


async def paginate_categories(categories: list[dict], elements_per_page: int = 3, page: int = 1) \
        -> (str, InlineKeyboardMarkup):
    limit = elements_per_page
    current_page = 1
    answer_text = ''
    keyboard = InlineKeyboardBuilder()

    for index, category in enumerate(categories):
        if limit == 0:
            limit = elements_per_page
            current_page += 1

        if current_page > page:
            break

        if page == current_page:
            text = await get_category_info(category)
            _id = category['_id']
            category_name = category['name']

            keyboard.row(InlineKeyboardButton(text=f'Категория "{category_name}"',
                                              callback_data=CategoryCallbackFactory(action='choose',
                                                                                    category_id=str(_id),
                                                                                    page=page).pack()))

            answer_text += text
        limit -= 1

    max_pages = math.ceil(len(categories) / elements_per_page)
    if max_pages == 1:
        return answer_text, keyboard.as_markup()
    buttons = list()

    if page - 1 != 0:
        buttons.append(InlineKeyboardButton(text='<', callback_data=f"categories_page:{page - 1}"))

    buttons.append(InlineKeyboardButton(text=f"{page}/{max_pages}", callback_data="None"))

    if page + 1 <= max_pages:
        buttons.append(InlineKeyboardButton(text='>', callback_data=f"categories_page:{page + 1}"))

    return answer_text, keyboard.row(*buttons).as_markup()


def current_category_keyboard(category_id: ObjectId,
                              page: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Добавить пользователя',
                                 callback_data=CategoryCallbackFactory(action='add_user',
                                                                       category_id=str(category_id),
                                                                       page=page).pack())
        ],
        [
            InlineKeyboardButton(text='Отправить сообщение',
                                 callback_data=CategoryCallbackFactory(action='send_message',
                                                                       category_id=str(category_id),
                                                                       page=page).pack())
        ],
        [
            InlineKeyboardButton(text='Задать область',
                                 callback_data=CategoryCallbackFactory(action='set_area',
                                                                       category_id=str(category_id),
                                                                       page=page).pack())
        ],
        [
            InlineKeyboardButton(text='Переименовать',
                                 callback_data=CategoryCallbackFactory(action='rename',
                                                                       category_id=str(category_id),
                                                                       page=page).pack()),
            InlineKeyboardButton(text='Удалить',
                                 callback_data=CategoryCallbackFactory(action='delete',
                                                                       category_id=str(category_id),
                                                                       page=page).pack())
        ],
        [
            InlineKeyboardButton(text='⬅️ Назад', callback_data=f'categories_page:{page}')
        ]
    ])
    return keyboard


def type_send_message(category_id: str,
                      page: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='С оповещением',
                                 callback_data=CategoryCallbackFactory(action='send_message_with_notify',
                                                                       category_id=category_id,
                                                                       page=page).pack()),
            InlineKeyboardButton(text='Без оповещения',
                                 callback_data=CategoryCallbackFactory(action='send_message_without_notify',
                                                                       category_id=category_id,
                                                                       page=page).pack())
        ]
    ])
    return keyboard


def accept_keyboard(category_id: ObjectId,
                    page: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Да, удалить',
                                 callback_data=CategoryCallbackFactory(action='accept_delete',
                                                                       category_id=str(category_id),
                                                                       page=page).pack()),
            InlineKeyboardButton(text='Нет',
                                 callback_data=CategoryCallbackFactory(action='choose',
                                                                       category_id=str(category_id),
                                                                       page=page).pack())
        ]
    ])
    return keyboard


class AcceptMessageCallbackFactory(CallbackData, prefix="accept_message"):
    action: str
    admin_id: int
    message_id: int


def accept_getting_message(admin_id,
                           message_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Я прочитал',
                                 callback_data=AcceptMessageCallbackFactory(action='read',
                                                                            admin_id=admin_id,
                                                                            message_id=message_id).pack())
        ]
    ])
    return keyboard
