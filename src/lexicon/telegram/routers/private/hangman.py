from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from callbacks.hangman import HangmanStartCallback
from keyboards import menu_keyboard as mk
from middlewares.private_middleware import PrivateChatMiddleware
from services.logic.games.hangman import HangmanService
from states.hangman import HangmanState

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
    callback: CallbackQuery, callback_data: HangmanStartCallback, state: FSMContext
):
    await callback.answer()
    await state.set_state(HangmanState.difficulty)
    await state.update_data(difficulty=callback_data.difficulty)

    await callback.message.edit_text(
        text=(
            "🎮 Игра началась!\n\n"
            f"{HANGMANPICS[0].strip()}\n\n"
            f"Слово: {show_word}\n\n"
            "Введите букву или угадайте слово целиком"
        )
    )


@router.message(StateFilter(HangmanState))
async def hangman_game_gameplay_handler(message: Message, state: FSMContext):
    result = await game_hangman_gameplay(message.from_user.id, message.text)
    print(result)
    if result[0] == "win":
        await state.clear()
        await message.answer(
            text=f"{result[1].strip()}\n\nСлово: {result[2]}\n\n🎉 Победа!",
            reply_markup=mk.back_to_menu_keyboard(),
        )
        await add_game_to_history(
            message.from_user.id,
            game_type="hangman",
            game_result=True,
            chat_id=message.chat.id,
        )
    elif result[0] == "lose":
        await state.clear()
        await message.answer(
            text=f"{result[1].strip()}\n\nСлово: {result[2]}\n\n😔 Поражение",
            reply_markup=mk.back_to_menu_keyboard(),
        )
        await add_game_to_history(
            message.from_user.id,
            game_type="hangman",
            game_result=False,
            chat_id=message.chat.id,
        )
    elif result[0] == "already_opened":
        await message.answer(
            text=f"{result[1].strip()}\n\nСлово: {result[2]}\n\n⚠️ Эта буква уже открыта",
        )
    elif result[0] == "Yes letter match":
        await message.answer(
            text=f"{result[1].strip()}\n\nСлово: {result[2]}\n\n✅ Есть в слове!",
        )
    elif result[0] == "No letter match":
        await message.answer(
            text=f"{result[1].strip()}\n\nСлово: {result[2]}\n\n❌ Нет в слове",
        )
    elif result[0] == "No word match":
        await message.answer(
            text=f"{result[1].strip()}\n\nСлово: {result[2]}\n\n❌ Слово не совпадает",
        )
