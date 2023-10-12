from aiogram import Bot
from aiogram.types import InputFile, Video, Document, Audio, Message

from tgbot.types import Album


class BadMessage(Exception):
    pass


class SimpleMessage:
    def __init__(self,
                 text: str = None,
                 photo: InputFile | list | str = None,
                 video: InputFile | Video | str = None,
                 document: InputFile | Document | str = None,
                 audio: InputFile | Audio | str = None,
                 album: Album = None):
        self.text = text
        self.photo = photo
        self.video = video
        self.document = document
        self.audio = audio
        self.album = album

        self.validate()

    def validate(self):
        if not any(self.__dict__.values()):
            raise BadMessage

        if not self.text:
            self.text = ''
        if isinstance(self.photo, list):
            self.photo = self.photo[-1].file_id
        if isinstance(self.video, Video):
            self.video = self.video.file_id
        if isinstance(self.document, Document):
            self.document = self.document.file_id
        if isinstance(self.audio, Audio):
            self.audio = self.audio.file_id

    async def send_to(self,
                      bot: Bot,
                      user_id: int,
                      reply_to_message_id: int | None = None):
        if self.album:
            album = self.album.as_media_group
            album[0].caption = self.text
            return await bot.send_media_group(chat_id=user_id,
                                              media=album,
                                              reply_to_message_id=reply_to_message_id)
        if self.photo:
            return await bot.send_photo(chat_id=user_id,
                                        photo=self.photo,
                                        caption=self.text,
                                        reply_to_message_id=reply_to_message_id)
        if self.video:
            return await bot.send_video(chat_id=user_id,
                                        video=self.video,
                                        caption=self.text,
                                        reply_to_message_id=reply_to_message_id)
        if self.document:
            return await bot.send_document(chat_id=user_id,
                                           document=self.document,
                                           caption=self.text,
                                           reply_to_message_id=reply_to_message_id)
        if self.audio:
            return await bot.send_audio(chat_id=user_id,
                                        audio=self.audio,
                                        caption=self.text,
                                        reply_to_message_id=reply_to_message_id)

        if self.text:
            return await bot.send_message(chat_id=user_id,
                                          text=self.text,
                                          reply_to_message_id=reply_to_message_id)

    @classmethod
    def create_by_other_message(cls,
                                message: Message,
                                album: Album = None):
        text = message.text if message.text else message.caption
        if album:
            return cls(text=text,
                       album=album)
        else:
            return cls(text=text,
                       photo=message.photo,
                       video=message.video,
                       audio=message.audio,
                       document=message.document)
