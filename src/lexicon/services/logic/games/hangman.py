from re import finditer

from entity.exceptions import GameLogicError, GameNotFound
from entity.uow import UnitOfWork

from src.lexicon.database.models.models import GameHistory, GameSessions


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


def game_logic(session_info: dict, user_attempt: str) -> dict:  # type: ignore
    word, attempt, opened_letters = session_info.values()
    user_attempt = user_attempt.lower()
    result = {
        "state": "",
        "pic": "",
        "opened_letters": "",
        "word": word,
        "attempt": attempt,
    }
    if len(user_attempt) == 1:
        matches = [
            m.start()
            for m in finditer(
                user_attempt,
                word,
            )
        ]
        if user_attempt in opened_letters:
            result.update(
                {
                    "opened_letters": "".join(opened_letters),
                    "pic": get_hangman_pic(attempt),
                    "state": "already_opened",
                }
            )
            return result
        if matches:
            for match in matches:
                opened_letters[match] = user_attempt
                if "".join(opened_letters) == word:
                    result.update(
                        {
                            "opened_letters": word,
                            "pic": get_hangman_pic(attempt),
                            "state": "win",
                        }
                    )
                    return result
                result.update(
                    {
                        "opened_letters": "".join(opened_letters),
                        "pic": get_hangman_pic(attempt),
                        "state": "letter_match",
                    }
                )
                return result
            else:
                attempt += 1
                if attempt == 6:
                    result.update(
                        {
                            "opened_letters": word,
                            "pic": get_hangman_pic(attempt),
                            "state": "lose",
                        }
                    )
                    return result
                result.update(
                    {
                        "opened_letters": "".join(opened_letters),
                        "pic": get_hangman_pic(attempt),
                        "state": "no_letter_match",
                    }
                )
                return result
    else:
        if user_attempt == word:
            result.update(
                {
                    "opened_letters": "".join(opened_letters),
                    "pic": get_hangman_pic(attempt),
                    "state": "win",
                }
            )
            return result
        else:
            attempt += 1
            if attempt == 6:
                result.update(
                    {
                        "opened_letters": word,
                        "pic": get_hangman_pic(attempt),
                        "state": "lose",
                    }
                )
                return result
            result.update(
                {
                    "opened_letters": "".join(opened_letters),
                    "pic": get_hangman_pic(attempt),
                    "state": "no_word_match",
                }
            )
            return result  # type: ignore #type: ignore


class HangmanService:
    uow: UnitOfWork

    def __init__(self, uow) -> None:
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
                "letters": opened_letters,
                "wordlen": len(word),
                "pic": get_hangman_pic(0),
            }
            await self.uow.commit()

            return res

    async def check_state(self, chat_id, user_id, user_attempt):
        async with self.uow:
            gamesesssion = await self.uow.gamesession.get_by_chat_id(chat_id)
            if gamesesssion is None:
                raise GameNotFound

            res = game_logic(gamesesssion.session_info, user_attempt=user_attempt)
            if res is None:
                raise GameLogicError
            if res["state"] == "lose" or res["state"] == "win":
                to_history = GameHistory(
                    chat_id=chat_id,
                    user_id=user_id,
                    game_type="hangman",
                    result=1 if res["state"] == "win" else 0,
                )
                await self.uow.gamesession.clear_by_chat_id(chat_id)
                await self.uow.gamehistory.add(to_history)
                return res
            gamesesssion.session_info.update(
                {
                    "attempt": res["attempt"],
                    "opened_letters": res["opened_letters"],
                }
            )
            await self.uow.commit()
            return res
