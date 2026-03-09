import logging
from re import finditer

from aiogram.types import game

from src.lexicon.database.models.models import GameHistory, GameSessions
from src.lexicon.services.entity.exceptions import GameLogicError, GameNotFound
from src.lexicon.services.entity.uow import UnitOfWork

logging = logging.getLogger(__name__)


def get_hangman_pic(attempt: int) -> str:
    HANGMAN_PICS = {
        0: r"""
    ┌─────┐
    │     │
            │
            │
            │
            │
    ═══════════
    """,
        1: r"""
    ┌─────┐
    │     │
    O     │
            │
            │
            │
    ═══════════
    """,
        2: r"""
    ┌─────┐
    │     │
    O     │
    │     │
            │
            │
    ═══════════
    """,
        3: r"""
    ┌─────┐
    │     │
    O     │
    ╱│     │
            │
            │
    ═══════════
    """,
        4: r"""
    ┌─────┐
    │     │
    O     │
    ╱│╲    │
            │
            │
    ═══════════
    """,
        5: r"""
    ┌─────┐
    │     │
    O     │
    ╱│╲    │
    ╱      │
            │
    ═══════════
    """,
        6: r"""
    ┌─────┐
    │     │
    O     │
    ╱│╲    │
    ╱ ╲    │
            │
    ═══════════
    """,
    }
    return HANGMAN_PICS[attempt]


def game_logic(session_info: dict, user_attempt: str) -> dict:
    word = session_info.get("word", "")
    attempt = session_info.get("attempt", 0)
    opened_letters = session_info.get("opened_letters", "")
    user_attempt = user_attempt.lower()
    result = {
        "state": "",
        "pic": "",
        "opened_letters": opened_letters,
        "word": word,
        "attempt": attempt,
    }

    # if letter
    if len(user_attempt) == 1:
        if user_attempt in opened_letters:
            result["state"] = "already_opened"
            result["pic"] = get_hangman_pic(attempt)
            return result
        if user_attempt in word:
            opened_list = list(opened_letters)
            for i, char in enumerate(word):
                if char == user_attempt:
                    opened_list[i] = user_attempt

            new_opened_letters = "".join(opened_list)
            result["opened_letters"] = new_opened_letters
            result["pic"] = get_hangman_pic(attempt)

            if new_opened_letters == word:
                result["state"] = "win"
            else:
                result["state"] = "letter_match"

            return result
        else:
            attempt += 1
            result["attempt"] = attempt
            result["pic"] = get_hangman_pic(attempt)

            if attempt == 6:
                result["state"] = "lose"
                result["opened_letters"] = (
                    word  # Показываем слово целиком при проигрыше
                )
            else:
                result["state"] = "no_letter_match"

            return result
    # if word
    else:
        if user_attempt == word:
            result["state"] = "win"
            result["pic"] = get_hangman_pic(attempt)

            return result

        else:
            attempt += 1
            result["attempt"] = attempt
            result["pic"] = get_hangman_pic(attempt)

            if attempt == 6:
                result["state"] = "lose"
                result["opened_letters"] = word
            else:
                result["state"] = "no_word_match"

            return result


class HangmanService:
    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def start_game(self, chat_id, user_id, difficulty) -> dict:  # type: ignore
        async with self.uow:
            await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
            if difficulty == "easy":
                word = await self.uow.hangman.get_random_easy()
            elif difficulty == "medium":
                word = await self.uow.hangman.get_random_medium()
            elif difficulty == "hard":
                word = await self.uow.hangman.get_random_hard()
            if word is None:
                raise GameLogicError
            attempt = 0
            opened_letters = list("_" * len(word))  # type: ignore
            session_info = {
                "word": word,
                "attempt": attempt,
                "opened_letters": opened_letters,
            }
            gamesession = GameSessions(
                chat_id=chat_id,
                session_info=session_info,
                user_id=user_id,
                game_type="hangman",
            )
            await self.uow.gamesession.add(gamesession)
            res = {
                "opened_letters": opened_letters,
                "wordlen": len(word),
                "pic": get_hangman_pic(0),
            }
            await self.uow.commit()
            logging.debug(f"Game started! Session info: {res}")
            return res

    async def check_state(self, chat_id, user_id, user_attempt):
        async with self.uow:
            gamesesssion = await self.uow.gamesession.get_by_chat_id(chat_id)
            if gamesesssion is None:
                logging.error("game not found")
                raise GameNotFound

            res = game_logic(gamesesssion.session_info, user_attempt=user_attempt)
            if res is None:
                logging.error(res)
                raise GameLogicError
            if res["state"] == "lose" or res["state"] == "win":
                to_history = GameHistory(
                    chat_id=chat_id,
                    user_id=user_id,
                    game_type="hangman",
                    game_result=1 if res["state"] == "win" else 0,
                )
                await self.uow.gamesession.clear_by_chat_id(chat_id)
                logging.debug(f" adding game to history: {to_history.__dict__}")
                await self.uow.gamehistory.add(to_history)
                logging.debug(f"{res['state']}!!!: {res}")
                await self.uow.commit()
                return res
            else:
                gamesesssion.session_info.update(
                    {
                        "attempt": res["attempt"],
                        "opened_letters": res["opened_letters"],
                    }
                )
                await self.uow.commit()
                logging.debug(f"checking state... Current state: {res}")
                return res
