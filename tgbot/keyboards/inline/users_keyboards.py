import math

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tgbot.db.db_api import roles


async def paginate_users(users_list: list[dict], elements_per_page: int = 10, page: int = 1) \
        -> (str, InlineKeyboardMarkup):
    limit = elements_per_page
    current_page = 1
    admin_text = '<b>Админы:</b>\n'
    user_text = '<b>Пользователи:</b>\n'

    admin_index, user_index = 0, 0
    admin_role = await roles.find_one({'name': 'admin'})
    user_role = await roles.find_one({'name': 'user'})

    keyboard = InlineKeyboardBuilder()

    for index, user in enumerate(users_list):
        if limit == 0:
            limit = elements_per_page
            current_page += 1

        if current_page > page:
            break

        if page == current_page:
            user_id = user['_id']
            name = user['name']

            mention = f'<a href="tg://user?id={user_id}">{name}</a>'

            if user['role'] == admin_role['_id']:
                admin_index += 1
                admin_text += f'{admin_index}. {mention} (ID: <code>{user_id}</code>)\n'

            elif user['role'] == user_role['_id']:
                user_index += 1
                user_text += f'{user_index}. {mention} (ID: <code>{user_id}</code>)\n'

        limit -= 1

    answer_text = (f'{admin_text}\n'
                   f'{user_text}')
    max_pages = math.ceil(len(users_list) / elements_per_page)
    if max_pages == 1:
        return answer_text, keyboard.as_markup()
    buttons = list()

    if page - 1 != 0:
        buttons.append(InlineKeyboardButton(text='<', callback_data=f"users_page:{page - 1}"))

    buttons.append(InlineKeyboardButton(text=f"{page}/{max_pages}", callback_data="None"))

    if page + 1 <= max_pages:
        buttons.append(InlineKeyboardButton(text='>', callback_data=f"users_page:{page + 1}"))

    return answer_text, keyboard.row(*buttons).as_markup()
