from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from tgbot.db.db_api import users, roles
from tgbot.keyboards.default.reply import admin_keyboard


class AuthorizationMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:

        user_id = event.from_user.id
        username = event.from_user.username
        name = event.from_user.full_name
        date = event.date

        user = await users.find_one({'_id': user_id})
        if user:
            return await handler(event, data)

        text = event.text if event.text else event.caption
        role = await roles.find_one({'password': text})
        if role:
            await users.insert_one({'_id': user_id,
                                    'username': username,
                                    'name': name,
                                    'date': date,
                                    'role': role['_id']})
            if role['name'] == 'admin':
                await event.answer(
                    '<b>Вы успешно авторизовались как админ. Используйте клавиатуру ⬇️</b>',
                    reply_markup=admin_keyboard)
            else:
                await event.answer('<b>Вы успешно авторизовались как пользователь.</b>')
