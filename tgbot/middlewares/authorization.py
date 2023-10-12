from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, html
from aiogram.types import Message

from tgbot.db.db_api import users, roles
from tgbot.db.service import get_instruction
from tgbot.keyboards.default.reply import admin_keyboard, user_keyboard
from tgbot.services.broadcaster import broadcast_admins


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

        print(await roles.find_one({'name': 'admin'}))

        text = event.text if event.text else event.caption
        role = await roles.find_one({'password': text})
        if role:
            instruction = await get_instruction()

            if role['name'] == 'admin':
                verbose_role = 'админ'
                await event.answer(text=f'<b>Вы успешно авторизовались как {verbose_role}.</b>\n'
                                        f'{html.quote(instruction)}',
                                   reply_markup=admin_keyboard)
            else:
                verbose_role = 'пользователь'
                await event.answer(text=f'<b>Вы успешно авторизовались как {verbose_role}.</b>\n'
                                        f'{html.quote(instruction)}',
                                   reply_markup=user_keyboard)

            await broadcast_admins(bot=event.bot,
                                   text=f'Добавился новый {html.bold(verbose_role)}: {event.from_user.mention_html()}')

            await users.insert_one({'_id': user_id,
                                    'username': username,
                                    'name': name,
                                    'date': date,
                                    'role': role['_id']})
