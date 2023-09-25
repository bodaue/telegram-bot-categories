from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='Категории'),
        KeyboardButton(text='Пользователи')
    ],
    [
        KeyboardButton(text='Настройки')
    ]
],
    resize_keyboard=True)
