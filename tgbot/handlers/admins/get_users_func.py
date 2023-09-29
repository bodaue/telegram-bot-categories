from aiogram import html


async def get_user_info(user: dict):
    user_id = user['_id']
    name = user['name']
    description = user.get('description', '')
    description = html.italic(description) if description else ''
    username = user.get('username', '')
    username = f'@{username}' if username else '-'

    mention = f'<a href="tg://user?id={user_id}">{name}</a>'

    text = (f'Пользователь {html.bold(mention)} (ID: {html.code(user_id)})\n'
            f'Юзернейм: {html.bold(username)}\n'
            f'{description}')

    return text
