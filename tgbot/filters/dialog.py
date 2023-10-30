from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot.config import Config
from tgbot.db.db_api import dialogs


class IsDialog(BaseFilter):
    async def __call__(self, obj: Message, config: Config):
        admin_id = obj.from_user.id
        dialog = await dialogs.find_one({'admin_id': admin_id,
                                         'admin_message_id': obj.reply_to_message.message_id})
        if dialog:
            return {'dialog': dialog}
        return False
