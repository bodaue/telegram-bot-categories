from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot.config import Config
from tgbot.db.db_api import users, roles


class AdminFilter(BaseFilter):
    async def __call__(self, obj: Message, config: Config) -> bool:
        user_id = obj.from_user.id
        admin_role = await roles.find_one({'name': 'admin'})
        if not admin_role:
            return False
        user = await users.find_one({'role': admin_role['_id'],
                                     '_id': user_id})
        return user
