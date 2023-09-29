from aiogram import Router, F, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.db.service import get_instruction
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.default.reply import admin_keyboard

admin_router = Router()
admin_router.message.filter(AdminFilter(), F.chat.type == "private")
admin_router.callback_query.filter(AdminFilter(), F.message.chat.type == "private")


@admin_router.message(Command(commands='start'))
async def admin_start(message: Message, state: FSMContext, user: dict):
    print(user)
    await state.clear()
    instruction = await get_instruction()
    await message.answer(html.quote(instruction),
                         reply_markup=admin_keyboard)
