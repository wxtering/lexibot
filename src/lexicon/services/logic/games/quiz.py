import logging
from random import choice

from src.lexicon.database.models.models import GameHistory, GameSessions
from src.lexicon.services.dto.quiz import QuizDTO, QuizState
from src.lexicon.services.entity.exceptions import GameLogicError, GameNotFound
from src.lexicon.services.entity.uow import UnitOfWork

logging = logging.getLogger(__name__)


async def get_random_quiz(uow: UnitOfWork) -> tuple[str, str]:
    res = await uow.quiz.get_random()
    if res is None:
        raise GameLogicError()
    return res.word, res.definition


def game_logic(session_info: dict, user_attempt: str) -> QuizDTO:
    word = session_info["word"]
    definition = session_info["definition"]
    attempts = session_info["attempts"]
    current_hint = "".join(session_info["hint_letters"])

    if word == user_attempt:
        return QuizDTO(
            state=QuizState.win,
            word=word,
            opened_letters=word,
            attempts=attempts,
            definition=definition,
        )

    attempts += 1
    logging.debug(f"attempts: {attempts}")

    if attempts % 3 == 0:
        hint = list(current_hint)
        closed = [i for i, ch in enumerate(hint) if ch == "_"]

        if closed:
            rnd = choice(closed)
            hint[rnd] = word[rnd]

        hint_letters = "".join(hint)

        if "_" not in hint_letters:
            return QuizDTO(
                state=QuizState.lose,
                word=word,
                opened_letters=word,
                attempts=attempts,
                definition=definition,
            )

        return QuizDTO(
            state=QuizState.hint,
            word=word,
            opened_letters=hint_letters,
            attempts=attempts,
            definition=definition,
        )

    return QuizDTO(
        state=QuizState.continue_,
        word=word,
        opened_letters=current_hint,
        attempts=attempts,
        definition=definition,
    )


async def get_hint(session_info: dict) -> str:
    word = session_info["word"]
    hint_list = list(session_info["hint_letters"])

    closed = [i for i, ch in enumerate(hint_list) if ch == "_"]
    if closed:
        rnd = choice(closed)
        hint_list[rnd] = word[rnd]

    return "".join(hint_list)


class QuizService:
    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def start_quiz(self, chat_id, user_id) -> QuizDTO:
        async with self.uow:
            await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
            word, definition = await get_random_quiz(self.uow)
            logging.debug(f"quiz started with word:{word}, definition:{definition}")

            hint_letters = "_" * len(word)
            session_info = {
                "word": word,
                "definition": definition,
                "attempts": 0,
                "hint_letters": list(hint_letters),
            }
            gamesession = GameSessions(
                chat_id=chat_id,
                user_id=user_id,
                session_info=session_info,
                game_type="quiz",
            )

            await self.uow.gamesession.add(gamesession)
            await self.uow.commit()
            logging.debug("game started successfully")

            return QuizDTO(
                state=QuizState.continue_,
                word=word,
                opened_letters=hint_letters,
                attempts=0,
                definition=definition,
            )

    async def check_state(self, chat_id, user_attempt, user_id) -> QuizDTO:
        async with self.uow:
            game_session = await self.uow.gamesession.get_by_chat_id(chat_id=chat_id)
            if not game_session:
                raise GameNotFound()

            logging.debug(f"session_info: {game_session.session_info}")
            info = game_logic(game_session.session_info, user_attempt)
            logging.debug(f"check game_logic result: {info}")

            if info.state == QuizState.win:
                to_history = GameHistory(
                    chat_id=chat_id,
                    user_id=user_id,
                    game_type="quiz",
                    game_result=1,
                )
                await self.uow.gamehistory.add(to_history)
                await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
                await self.uow.commit()
                return info

            if info.state == QuizState.continue_:
                game_session.session_info.update(
                    {
                        "attempts": info.attempts,
                    }
                )
                await self.uow.commit()
                logging.debug(f"continue section attempts={info.attempts}")
                return info

            if info.state == QuizState.hint:
                game_session.session_info.update(
                    {
                        "hint_letters": list(info.opened_letters),
                        "attempts": info.attempts,
                    }
                )
                logging.debug("hint section")
                await self.uow.commit()
                return info

            if info.state == QuizState.lose:
                await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
                await self.uow.commit()
                return info

            raise GameLogicError()

    async def hint(self, chat_id: int) -> str:
        async with self.uow:
            game_session = await self.uow.gamesession.get_by_chat_id(chat_id=chat_id)
            if not game_session:
                raise GameNotFound()

            hint = await get_hint(game_session.session_info)
            game_session.session_info.update({"hint_letters": list(hint)})
            await self.uow.commit()
            return hint

    async def quit_game(self, chat_id: int) -> None:
        async with self.uow:
            await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
            await self.uow.commit()
