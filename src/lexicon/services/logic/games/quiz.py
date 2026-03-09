import logging
from random import choice

from src.lexicon.database.models.models import GameHistory, GameSessions
from src.lexicon.services.entity.exceptions import GameLogicError, GameNotFound
from src.lexicon.services.entity.uow import UnitOfWork

logging = logging.getLogger(__name__)


async def get_random_quiz(uow: UnitOfWork) -> tuple[str, str]:
    res = await uow.quiz.get_random()
    return res.word, res.definition  # type:ignore


def game_logic(session_info: dict, user_attempt: str) -> dict:
    word = session_info["word"]

    if word == user_attempt:
        res = {"data": {}, "response": {"word": word, "state": "win"}}
        return res
    else:
        attempts = session_info["attempts"] + 1
        logging.debug(f"attempts: {attempts}")
        if (attempts - 3) % 3 == 0:
            hint = list(session_info["hint_letters"])
            closed = [i for i, ch in enumerate(hint) if ch == "_"]

            if closed:
                rnd = choice(closed)
                hint[rnd] = word[rnd]

            hint_letters = "".join(hint)

            if "_" not in hint_letters:
                res = {
                    "data": {
                        "hint_letters": hint_letters,
                        "attempts": attempts,
                    },
                    "response": {
                        "state": "lose",
                        "word": word,
                        "hint_letters": hint_letters,
                    },
                }
                return res

            res = {
                "data": {
                    "hint_letters": hint_letters,
                    "attempts": attempts,
                },
                "response": {
                    "state": "hint",
                    "word": word,
                    "hint_letters": hint_letters,
                },
            }
            return res
        else:
            res = {
                "data": {
                    "attempts": attempts,
                },
                "response": {
                    "word": word,
                    "state": "continue",
                },
            }
            return res


async def get_hint(session_info) -> str:
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

    async def start_quiz(self, chat_id, user_id) -> dict:
        async with self.uow:
            await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
            word, definition = await get_random_quiz(self.uow)
            logging.debug(f"quiz started with word:{word}, definition:{definition}")
            session_info = {
                "word": word,
                "definition": definition,
                "attempts": 0,
                "hint_letters": list(len(word) * "_"),
            }
            gamesession = GameSessions(
                chat_id=chat_id,
                user_id=user_id,
                session_info=session_info,
                game_type="quiz",
            )
            await self.uow.gamesession.add(gamesession)
            res = {"definition": definition, "wordlen": len(word)}
            await self.uow.commit()
            logging.debug("game started successfully")
            return res

    async def check_state(self, chat_id, user_attempt, user_id) -> dict:
        async with self.uow:
            game_session = await self.uow.gamesession.get_by_chat_id(chat_id=chat_id)
            logging.debug(f"session_info: {game_session.session_info}")
            if not game_session:
                raise GameNotFound()

            info = game_logic(game_session.session_info, user_attempt)
            logging.debug(f"check game_logic result: {info}")
            if info["response"]["state"] == "win":
                to_history = GameHistory(
                    chat_id=chat_id,
                    user_id=user_id,
                    game_type="quiz",
                    game_result=1,
                )
                await self.uow.gamehistory.add(to_history)
                await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
                await self.uow.commit()
                return info["response"]
            elif info["response"]["state"] == "continue":
                game_session.session_info.update(
                    {
                        "attempts": info["data"]["attempts"],
                    }
                )
                await self.uow.commit()
                logging.debug(f"continue section {info['data']}")
                return info["response"]
            elif info["response"]["state"] == "hint":
                game_session.session_info.update(
                    {
                        "hint_letters": info["data"]["hint_letters"],
                        "attempts": info["data"]["attempts"],
                    }
                )
                logging.debug("hint section")
                await self.uow.commit()
                return info["response"]
            elif info["response"]["state"] == "lose":
                await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
                await self.uow.commit()
                return info["response"]
            else:
                raise GameLogicError()

    async def hint(self, chat_id) -> str:
        async with self.uow:
            game_session = await self.uow.gamesession.get_by_chat_id(chat_id=chat_id)
            if not game_session:
                raise GameNotFound()

            hint = await get_hint(game_session.session_info)
            game_session.session_info.update({"hint_letters": hint})
            await self.uow.commit()
            return hint

    async def quit_game(self, chat_id: int) -> None:
        async with self.uow:
            await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
            await self.uow.commit()
