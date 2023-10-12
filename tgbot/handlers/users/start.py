from datetime import datetime, timezone, timedelta

from aiogram import Router, F, Bot, html
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.db.db_api import dialogs
from tgbot.db.service import get_instruction, get_admins
from tgbot.keyboards.default.reply import user_keyboard
from tgbot.keyboards.inline.categories_keyboards import AcceptMessageCallbackFactory
from tgbot.types import Album
from tgbot.types.simple_message import SimpleMessage

user_router = Router()
user_router.message.filter(F.chat.type == "private")
user_router.callback_query.filter(F.message.chat.type == 'private')


@user_router.message(CommandStart(), flags={'throttling_key': 'default'})
async def user_start(message: Message, state: FSMContext):
    instruction = await get_instruction()
    await message.answer(text=html.quote(instruction),
                         reply_markup=user_keyboard)
    await state.clear()


@user_router.message(F.text == 'Отправить контент')
async def send_content(message: Message, state: FSMContext):
    await state.set_state('waiting_content')
    await message.answer(html.bold('Отправьте контент, который хотите отправить администраторам.'))


@user_router.message(StateFilter('waiting_content'))
async def waiting_content(message: Message, bot: Bot, state: FSMContext, album: Album = None):
    await state.clear()

    msg = SimpleMessage.create_by_other_message(message=message,
                                                album=album)
    msg.text = (f'Пользователь {message.from_user.mention_html()} отправил это сообщение\n\n'
                f''
                f'{msg.text}')

    admins = await get_admins()
    for admin in admins:
        await msg.send_to(bot=bot,
                          user_id=admin['_id'])
    await message.reply('Сообщение отправлено')


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


@user_router.message(F.reply_to_message)
async def reply_to_message(message: Message, bot: Bot):
    user_id = message.from_user.id
    dialog = await dialogs.find_one({'user_id': user_id,
                                     'user_message_id': message.reply_to_message.message_id})

    if dialog:
        admin_id = dialog['admin_id']
        admin_message_id = dialog['admin_message_id']
        msg = SimpleMessage.create_by_other_message(message=message)
        msg.text = (f'Пользователь {message.from_user.mention_html()} отправил это сообщение\n\n'
                    f''
                    f'{msg.text}')
        m = await msg.send_to(bot=bot,
                              user_id=admin_id,
                              reply_to_message_id=admin_message_id)
        await dialogs.update_one(filter={'user_id': user_id,
                                         'user_message_id': message.reply_to_message.message_id,
                                         'admin_id': dialog['admin_id']},
                                 update={'$set': {'admin_message_id': m.message_id}})
