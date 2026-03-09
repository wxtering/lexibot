from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from src.lexicon.services.logic.games.quiz import QuizService
from src.lexicon.services.logic.user import UserService
from src.lexicon.tg_bot.middlewares.chat import GroupChatMiddleware
from src.lexicon.tg_bot.states.quiz import QuizState

router = Router()
router.message.middleware(GroupChatMiddleware())
router.callback_query.middleware(GroupChatMiddleware())


@router.message(Command("quiz"))
async def quiz_start(
    message: Message,
    state: FSMContext,
    QuizService: FromDishka[QuizService],
    UserService: FromDishka[UserService],
):
    await state.set_state(QuizState.ingame)
    game_session = await QuizService.start_quiz(
        chat_id=message.chat.id, user_id=message.from_user.id
    )
    await UserService.add_user(
        username=message.from_user.username, user_id=message.from_user.id
    )
    await message.answer(
        text=(
            f"📖 Новый вопрос!\n\n"
            f"{game_session['definition']}\n\n"
            f"🔤 Слово из {game_session['wordlen']} букв\n"
            f"💡 Напишите ответ в формате: 'слово'\n"
            f"🔍 Подсказка: напишите hint"
        ),
    )


@router.message(QuizState.ingame, Command("quit"))
async def quit(
    message: Message, state: FSMContext, QuizService: FromDishka[QuizService]
):
    await state.clear()
    await QuizService.quit_game(chat_id=message.chat.id)
    await message.answer(text="🛑 Игра завершена. До встречи!")


@router.message(QuizState.ingame, F.text.startswith("hint"))
async def get_hint(
    message: Message, state: FSMContext, QuizService: FromDishka[QuizService]
):
    hint = await QuizService.hint(chat_id=message.chat.id)
    await message.answer(
        text=f"🔍 Подсказка:\n\n{hint}",
    )


@router.message(QuizState.ingame)
async def quiz_answer(
    message: Message,
    state: FSMContext,
    QuizService: FromDishka[QuizService],
    UserService: FromDishka[UserService],
):
    answer = message.text.lower()
    result = await QuizService.check_state(
        user_attempt=answer, chat_id=message.chat.id, user_id=message.from_user.id
    )
    if result["state"] == "Continue":
        pass
    elif result["state"] == "win":
        await UserService.add_user(
            username=message.from_user.username, user_id=message.from_user.id
        )
        await message.answer(
            text=f"✅ Правильно!\n\nСлово: {result['word']}",
        )

    elif result["state"] == "hint":
        await message.answer(
            text=f"🔍 Подсказка:\n{result['hint_letters']}",
        )
    elif result["state"] == "lose":
        await message.answer(
            text=f"❌ Вы проиграли!, слово было: {result['word']}",
        )
