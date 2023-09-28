from datetime import datetime, timezone, timedelta

from aiogram import Router, F, Bot, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.db.service import get_instruction
from tgbot.keyboards.inline.categories_keyboards import AcceptMessageCallbackFactory

user_router = Router()
user_router.message.filter(F.chat.type == "private")
user_router.callback_query.filter(F.message.chat.type == 'private')


@user_router.message(CommandStart(), flags={'throttling_key': 'default'})
async def user_start(message: Message, state: FSMContext):
    instruction = await get_instruction()
    await message.answer(html.quote(instruction))
    await state.clear()


@user_router.callback_query(AcceptMessageCallbackFactory.filter(F.action == 'read'))
async def accept_getting_message(call: CallbackQuery, callback_data: AcceptMessageCallbackFactory, bot: Bot):
    admin_id = callback_data.admin_id
    message_id = callback_data.message_id

    mention = call.from_user.mention_html()

    date = datetime.now(tz=timezone(timedelta(hours=3), name='Europe/Moscow'))
    date = date.strftime('%d.%m.%Y %H:%M')
    await bot.send_message(chat_id=admin_id,
                           reply_to_message_id=message_id,
                           text=f'<b>{mention}</b> прочитал сообщение.\n'
                                f'<b>Дата:</b> {date}')
    await call.message.delete_reply_markup()
