import re

import textract as textract
from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message
from docx import Document
from pypdf import PdfReader

from tgbot.config import Config
from tgbot.services.point import Point
from tgbot.types.mimetype import MimeType

TXT_PATH = '/root/bot_categories/tgbot/downloaded_files/txt/'
PDF_PATH = '/root/bot_categories/tgbot/downloaded_files/pdf/'
DOCX_PATH = '/root/bot_categories/tgbot/downloaded_files/docx/'
PHOTOS_PATH = '/root/bot_categories/tgbot/downloaded_files/photos/'


# TXT_PATH = 'tgbot/downloaded_files/txt/'
# PDF_PATH = 'tgbot/downloaded_files/pdf/'
# DOCX_PATH = 'tgbot/downloaded_files/docx/'
# PHOTOS_PATH = 'tgbot/downloaded_files/photos/'


class HasCords(BaseFilter):
    async def __call__(self, message: Message, bot: Bot, config: Config):
        text = message.text if message.text else message.caption if message.caption else ''
        text += '\n'
        document = message.document
        photo = message.photo
        if document:
            if document.mime_type == MimeType.TXT.value:
                await bot.download(file=document.file_id,
                                   destination=TXT_PATH + document.file_name)
                with open(TXT_PATH + document.file_name, 'r') as file:
                    txt_text = file.read()
                    text += txt_text
            elif document.mime_type == MimeType.PDF.value:
                await bot.download(file=document.file_id,
                                   destination=PDF_PATH + document.file_name)
                reader = PdfReader(PDF_PATH + document.file_name)
                pdf_text = ''
                for page in reader.pages:
                    pdf_text += page.extract_text() + '\n'
                text += pdf_text

            elif document.mime_type == MimeType.DOCX.value:
                await bot.download(file=document.file_id,
                                   destination=DOCX_PATH + document.file_name)
                document = Document(DOCX_PATH + document.file_name)
                docx_text = '\n'.join([p.text for p in document.paragraphs])
                text += docx_text

            elif document.mime_type == MimeType.DOC.value:
                await bot.download(file=document.file_id,
                                   destination=DOCX_PATH + document.file_name)
                doc_text = textract.process(DOCX_PATH + document.file_name)
                doc_text = doc_text.decode('utf-8')
                text += doc_text

            elif document.mime_type in (MimeType.JPG.value, MimeType.PNG.value):
                await bot.download(file=document.file_id,
                                   destination=PHOTOS_PATH + document.file_name)

                photo_text = textract.process(PHOTOS_PATH + document.file_name)
                photo_text = photo_text.decode('utf-8')
                text += photo_text

        elif photo:
            photo = photo[-1]
            await bot.download(file=photo.file_id,
                               destination=PHOTOS_PATH + photo.file_id + '.jpg')
            photo_text = textract.process(PHOTOS_PATH + photo.file_id + '.jpg')
            photo_text = photo_text.decode('utf-8')
            text += photo_text
        points = self._parse_cords(text=text)
        print(points)
        if points:
            return {'points': [Point(*point) for point in points]}
        return False

    @staticmethod
    def _parse_cords(text):
        comp = re.compile(pattern=r'(\d+\.\d+),\s*(\d+\.\d+)')
        found = comp.findall(string=text)
        cords = [[float(j) for j in i] for i in found]
        return cords
