from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.db.db_api import categories
from tgbot.handlers.admins.categories_handlers.categories_func import get_category_info
from tgbot.keyboards.inline.categories_keyboards import current_category_keyboard

creating_category_router = Router()


# Ветка "Создать новую категорию"
@creating_category_router.callback_query(F.data == 'create_category')
async def create_category(call: CallbackQuery, state: FSMContext):
    await call.message.answer('Отправьте название категории')
    await state.set_state('waiting_category_name')


@creating_category_router.message(StateFilter('waiting_category_name'), F.text)
async def waiting_category_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    date = message.date

    name = message.text.strip()
    if len(name) > 64:
        await message.answer('Длина названия не может превышать 64 символов!')
        return

    category = await categories.find_one({'name': name})
    if category:
        await message.answer('Категория с таким названием уже существует!')
        return

    new_category = await categories.insert_one({'created_by': user_id,
                                                'name': name,
                                                'date': date})
    _id = new_category.inserted_id
    category = await categories.find_one({'_id': _id})
    text = await get_category_info(category)

    await message.answer(f'Категория <b>{name}</b> успешно создана!')
    await message.answer(text=text,
                         reply_markup=current_category_keyboard(category_id=_id,
                                                                page=1))
    await state.clear()
