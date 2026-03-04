from random import choice

from database.models.models import GameHistory, GameSessions
from entity.exceptions import GameLogicError, GameNotFound
from entity.uow import UnitOfWork
from sqlalchemy.sql.functions import user


async def get_random_quiz(uow: UnitOfWork) -> tuple[str, str]:
    res = await uow.quiz.get_random()
    return res.word, res.definition  # type:ignore


def game_logic(session_info: dict, user_attempt: str) -> dict:
    word = session_info["word"]
    answer = user_attempt

    if word == answer:
        res = {"data": {}, "response": {"word": word, "state": "win"}}
        return res
    else:
        attempts = session_info["attempts"] + 1

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


async def get_hint(game_session) -> str:
    word = game_session["word"]
    hint_list = list(game_session["hint_letters"])

    closed = [i for i, ch in enumerate(hint_list) if ch == "_"]
    if closed:
        rnd = choice(closed)
        hint_list[rnd] = word[rnd]

    return "".join(hint_list)


class QuizService:
    uow: UnitOfWork

    def __init__(self, uow) -> None:
        self.uow = uow

    async def start_quiz(self, chat_id, user_id) -> dict:
        async with self.uow:
            await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
            word, definition = await get_random_quiz(self.uow)
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
            )
            await self.uow.gamesession.add(gamesession)
            res = {"definition": definition, "wordlen": len(word)}
            return res

    async def check_state(self, chat_id, user_attempt, user_id) -> dict:
        async with self.uow:
            game_session = await self.uow.gamesession.get_by_chat_id(chat_id=chat_id)
            if not game_session:
                raise GameNotFound()

            info = game_logic(game_session.session_info, user_attempt)
            if info["response"]["state"] == "win":
                to_history = GameHistory(
                    chat_id=chat_id,
                    user_id=user_id,
                    game_type="hangman",
                    result=1,
                )
                await self.uow.gamehistory.add(to_history)
                await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)

                return info["response"]
            elif info["response"]["state"] == "continue":
                game_session.session_info.update(
                    {
                        "attempts": info["data"]["attempts"],
                        "hint_letters": info["data"]["hint_letters"],
                    }
                )
                return info["response"]
            elif info["response"]["state"] == "hint":
                return info["response"]
            elif info["response"]["state"] == "lose":
                await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
                to_history = GameHistory(
                    chat_id=chat_id,
                    user_id=user_id,
                    game_type="hangman",
                    result=0,
                )
                await self.uow.gamehistory.add(to_history)
                await self.uow.gamesession.clear_by_chat_id(chat_id)
                await self.uow.commit()
                return info["response"]
            else:
                raise GameLogicError()

    async def hint(self, chat_id) -> str:
        async with self.uow:
            game_session = await self.uow.gamesession.get_by_chat_id(chat_id=chat_id)
            if not game_session:
                raise GameNotFound()

            hint = await get_hint(game_session)
            game_session.session_info.update({"hint_letters": hint})
            await self.uow.commit()
            return hint
