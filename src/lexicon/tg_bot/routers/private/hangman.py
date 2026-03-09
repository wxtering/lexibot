import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from src.lexicon.services.dto.hangman import HangmanState
from src.lexicon.services.logic.games.hangman import HangmanService
from src.lexicon.services.logic.user import UserService
from src.lexicon.tg_bot.callbacks.hangman import HangmanStartCallback
from src.lexicon.tg_bot.keyboards import menu_keyboard as mk
from src.lexicon.tg_bot.middlewares.private import PrivateChatMiddleware
from src.lexicon.tg_bot.states.hangman import HangmanFsmState

logging = logging.getLogger(__name__)
router = Router()
router.message.middleware(PrivateChatMiddleware())
router.callback_query.middleware(PrivateChatMiddleware())


def get_hangman_pic(attempt: int) -> str:
    HANGMAN_PICS = {
        0: ("┌─────┐\n│     │\n│      \n│      \n│      \n│      \n└──────"),
        1: ("┌─────┐\n│     │\n│     O\n│      \n│      \n│      \n└──────"),
        2: ("┌─────┐\n│     │\n│     O\n│     │\n│      \n│      \n└──────"),
        3: ("┌─────┐\n│     │\n│     O\n│    ╱│\n│      \n│      \n└──────"),
        4: ("┌─────┐\n│     │\n│     O\n│    ╱│╲\n│      \n│      \n└──────"),
        5: ("┌─────┐\n│     │\n│     O\n│    ╱│╲\n│    ╱ \n│      \n└──────"),
        6: ("┌─────┐\n│     │\n│     O\n│    ╱│╲\n│    ╱ ╲\n│      \n└──────"),
    }
    return HANGMAN_PICS[attempt]


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
    await state.set_state(HangmanFsmState.difficulty)
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
            f"{get_hangman_pic(game_session.attempts)}\n\n"
            f"Слово: {game_session.opened_letters}\n\n"
            "Введите букву или угадайте слово целиком"
        )
    )


@router.message(StateFilter(HangmanFsmState))
async def hangman_game_gameplay_handler(
    message: Message, state: FSMContext, HangmanService: FromDishka[HangmanService]
):

    user_answer = message.text.lower()
    game_session = await HangmanService.check_state(
        user_id=message.from_user.id, chat_id=message.chat.id, user_attempt=user_answer
    )
    if game_session.state == HangmanState.lose:
        await state.clear()
        await message.answer(
            text=f"{get_hangman_pic(game_session.attempts)}\n\nСлово: {game_session.word}\n\n😔 Поражение",
            reply_markup=mk.back_to_menu_keyboard(),
        )
    elif game_session.state == HangmanState.win:
        await message.answer(
            text=f"{get_hangman_pic(game_session.attempts)}\n\nСлово: {game_session.opened_letters}\n\nПобеда!",
            reply_markup=mk.back_to_menu_keyboard(),
        )
    elif game_session.state == HangmanState.already_opened:
        await message.answer(
            text=f"{get_hangman_pic(game_session.attempts)}\n\nСлово: {game_session.opened_letters}\n\n⚠️ Эта буква уже открыта",
        )
    elif game_session.state == HangmanState.letter_match:
        await message.answer(
            text=f"{get_hangman_pic(game_session.attempts)}\n\nСлово: {game_session.opened_letters}\n\n✅ Есть в слове!",
        )
    elif game_session.state == HangmanState.no_letter_match:
        await message.answer(
            text=f"{get_hangman_pic(game_session.attempts)}\n\nСлово: {game_session.opened_letters}\n\n❌ Нет в слове",
        )
    elif game_session.state == HangmanState.no_word_match:
        await message.answer(
            text=f"{get_hangman_pic(game_session.attempts)}\n\nСлово: {game_session.opened_letters}\n\n❌ Слово не совпадает",
        )
