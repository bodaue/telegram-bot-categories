from aiogram import Router, F, html
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.db.db_api import roles, settings
from tgbot.db.service import get_instruction
from tgbot.keyboards.inline.settings_keyboards import edit_settings_keyboard, PasswordCallbackFactory

admin_settings_router = Router()

MINIMUM_INSTRUCTION_LENGTH = 4
MAXIMUM_INSTRUCTION_LENGTH = 4000

MINIMUM_PASSWORD_LENGTH = 4
MAXIMUM_PASSWORD_LENGTH = 64


@admin_settings_router.message(F.text == 'Настройки')
async def get_settings(message: Message):
    instruction = await get_instruction()

    admin_password = (await roles.find_one({'name': 'admin'}))['password']
    user_password = (await roles.find_one({'name': 'user'}))['password']

    text = (f'<b>Текст для инструкции:</b>\n'
            f'{html.quote(instruction)}\n\n'
            f'<b>Админ пароль:</b> {html.code(html.quote(admin_password))}\n'
            f'<b>Пользовательский пароль:</b> {html.code(html.quote(user_password))}')
    await message.answer(text=text,
                         reply_markup=edit_settings_keyboard)


@admin_settings_router.callback_query(F.data == 'change_instruction')
async def change_instruction(call: CallbackQuery,
                             state: FSMContext):
    await state.set_state('waiting_instruction')
    await call.answer('Отправьте новый текст инструкции')


@admin_settings_router.message(StateFilter('waiting_instruction'))
async def waiting_instruction(message: Message, state: FSMContext):
    instruction = message.text.strip()
    if len(instruction) < MINIMUM_INSTRUCTION_LENGTH:
        await message.answer(f'Минимальная длина инструкции: {MINIMUM_INSTRUCTION_LENGTH} символа')
        return
    if len(instruction) > MAXIMUM_INSTRUCTION_LENGTH:
        await message.answer(f'Максимальная длина инструкции: {MAXIMUM_INSTRUCTION_LENGTH} символа')
        return

    await settings.update_one(filter={'name': 'instruction'},
                              update={'$set': {'text': instruction}})

    await message.answer('Вы изменили инструкцию!')
    await state.clear()
    await get_settings(message=message)


@admin_settings_router.callback_query(PasswordCallbackFactory.filter(F.action == 'change'))
async def change_password(call: CallbackQuery,
                          callback_data: PasswordCallbackFactory,
                          state: FSMContext):
    role = callback_data.role
    await state.set_state('waiting_new_password')
    await state.update_data(role=role)
    await call.answer('Отправьте новый пароль')


@admin_settings_router.message(StateFilter('waiting_new_password'), F.text)
async def waiting_new_password(message: Message,
                               state: FSMContext):
    password = message.text.strip()
    if len(password) < MINIMUM_PASSWORD_LENGTH:
        await message.answer(f'Минимальная длина пароля: {MINIMUM_PASSWORD_LENGTH} символа')
        return
    if len(password) > MAXIMUM_PASSWORD_LENGTH:
        await message.answer(f'Максимальная длина пароля: {MAXIMUM_PASSWORD_LENGTH} символа')
        return

    data = await state.get_data()
    role = data.get('role')
    await roles.update_one({'name': role},
                           {'$set': {'password': password}})
    await message.answer('Вы изменили пароль!')
    await state.clear()
    await get_settings(message=message)
