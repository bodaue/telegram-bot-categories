from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from tgbot.db.db_api import users


class UpdateUserDataMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:

        user_id = event.from_user.id
        username = event.from_user.username
        name = event.from_user.full_name

        user = await users.find_one({'_id': user_id})
        data['user'] = user

        if user:
            if user.get('username') != username:
                await users.update_one({'_id': user_id},
                                       {'$set': {'username': username}})
            if user.get('name') != name:
                await users.update_one({'_id': user_id},
                                       {'$set': {'name': name}})
        return await handler(event, data)
