from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class PasswordCallbackFactory(CallbackData, prefix="password"):
    action: str
    role: str


change_password_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Изменить админ пароль',
                             callback_data=PasswordCallbackFactory(action='change',
                                                                   role='admin').pack())
    ],
    [
        InlineKeyboardButton(text='Изменить пользовательский пароль',
                             callback_data=PasswordCallbackFactory(action='change',
                                                                   role='user').pack())
    ]
])
