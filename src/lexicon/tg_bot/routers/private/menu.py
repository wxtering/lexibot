import logging

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.lexicon.services.logic.user import UserService
from src.lexicon.tg_bot.keyboards import menu_keyboard as mk
from src.lexicon.tg_bot.middlewares.private import PrivateChatMiddleware

logging = logging.getLogger(__name__)
router = Router()
router.message.middleware(PrivateChatMiddleware())
router.callback_query.middleware(PrivateChatMiddleware())


@router.message(Command("start"), StateFilter(None))
async def start_command(message: Message, UserService: FromDishka[UserService]):
    await message.answer(
        text="👋 Привет!\n\nЯ бот для словесных игр. Выбери игру в меню ниже.",
        reply_markup=mk.back_to_menu_keyboard(),
    )
    await UserService.add_user(
        username=message.from_user.username, user_id=message.from_user.id
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_command(callback: CallbackQuery):
    await callback.message.edit_text(
        text="📋 Главное меню", reply_markup=mk.get_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "game_selection")
async def game_selection_command(callback: CallbackQuery):
    await callback.message.edit_text(
        text="🎮 Выберите игру:",
        reply_markup=mk.game_selection_keyboard(),
    )
    await callback.answer()
