from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot.config import Config


class FileExtension(BaseFilter):

    def __init__(self, mime_type: str):
        self.mime_type = mime_type

    async def __call__(self, obj: Message, config: Config) -> bool:
        if not obj.document:
            return False

        return self.mime_type == obj.document.mime_type
