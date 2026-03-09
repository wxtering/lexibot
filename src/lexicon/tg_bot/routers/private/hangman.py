import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka
from services.logic.games.hangman import HangmanService
from services.logic.user import UserService
from tg_bot.callbacks.hangman import HangmanStartCallback
from tg_bot.keyboards import menu_keyboard as mk
from tg_bot.middlewares.private import PrivateChatMiddleware
from tg_bot.states.hangman import HangmanState

logging = logging.getLogger(__name__)
router = Router()
router.message.middleware(PrivateChatMiddleware())
router.callback_query.middleware(PrivateChatMiddleware())


@router.callback_query(F.data == "hangman_difficulty")
async def hangman_difficulty_command(callback: CallbackQuery):
    await callback.message.edit_text(
        text="🎯 Выберите сложность\n\nКоличество букв в слове:\n• Легкий — 5 букв\n• Средний — 6–8 букв\n• Сложный — 9–14 букв",
        reply_markup=mk.hangman_difficulty_keyboard(),
    )
    await callback.answer()


@router.callback_query(HangmanStartCallback.filter())
async def hangman_game_start_handler(
    callback: CallbackQuery,
    callback_data: HangmanStartCallback,
    state: FSMContext,
    UserService: FromDishka[UserService],
    HangmanService: FromDishka[HangmanService],
):
    await callback.answer()
    await state.set_state(HangmanState.difficulty)
    await state.update_data(difficulty=callback_data.difficulty)
    await UserService.add_user(
        user_id=callback.from_user.id, username=callback.from_user.username
    )
    game_session = await HangmanService.start_game(
        user_id=callback.from_user.id,
        chat_id=callback.message.chat.id,
        difficulty=callback_data.difficulty,
    )
    await callback.message.edit_text(
        text=(
            "🎮 Игра началась!\n\n"
            f"{game_session['pic']}\n\n"
            f"Слово: {game_session['opened_letters']}\n\n"
            "Введите букву или угадайте слово целиком"
        )
    )


@router.message(StateFilter(HangmanState))
async def hangman_game_gameplay_handler(
    message: Message, state: FSMContext, HangmanService: FromDishka[HangmanService]
):

    user_answer = message.text.lower()
    game_session = await HangmanService.check_state(
        message.from_user.id, message.chat.id, user_answer
    )
    if game_session["state"] == "win":
        await state.clear()
        await message.answer(
            text=f"{game_session['pic'].strip()}\n\nСлово: {game_session['word']}\n\n🎉 Победа!",
            reply_markup=mk.back_to_menu_keyboard(),
        )
    elif game_session["state"] == "lose":
        await state.clear()
        await message.answer(
            text=f"{game_session['pic'].strip()}\n\nСлово: {game_session['word']}\n\n😔 Поражение",
            reply_markup=mk.back_to_menu_keyboard(),
        )
    elif game_session["state"] == "already_opened":
        await message.answer(
            text=f"{game_session['pic'].strip()}\n\nСлово: {game_session['opened_letters']}\n\n⚠️ Эта буква уже открыта",
        )
    elif game_session["state"] == "letter_match":
        await message.answer(
            text=f"{game_session['pic'].strip()}\n\nСлово: {game_session['opened_letters']}\n\n✅ Есть в слове!",
        )
    elif game_session["state"] == "no_letter_match":
        await message.answer(
            text=f"{game_session['pic'].strip()}\n\nСлово: {game_session['opened_letters']}\n\n❌ Нет в слове",
        )
    elif game_session["state"] == "no_word_match":
        await message.answer(
            text=f"{game_session['pic'].strip()}\n\nСлово: {game_session['opened_letters']}\n\n❌ Слово не совпадает",
        )
