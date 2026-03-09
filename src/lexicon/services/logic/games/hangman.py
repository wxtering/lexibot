import logging

from src.lexicon.database.models.models import GameHistory, GameSessions
from src.lexicon.services.dto.hangman import HangmanDTO, HangmanState
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


def game_logic(session_info: dict, user_attempt: str) -> HangmanDTO:
    word = session_info.get("word", "")
    attempt = session_info.get("attempt", 0)
    opened_letters = session_info.get("opened_letters", "")
    user_attempt = user_attempt.lower()

    if len(user_attempt) == 1:
        if user_attempt in opened_letters:
            return HangmanDTO(
                state=HangmanState.already_opened,
                word=None,
                opened_letters=opened_letters,
                attempts=attempt,
            )
        if user_attempt in word:
            opened_list = list(opened_letters)
            for i, char in enumerate(word):
                if char == user_attempt:
                    opened_list[i] = user_attempt

            new_opened_letters = "".join(opened_list)

            if new_opened_letters == word:
                return HangmanDTO(
                    state=HangmanState.win,
                    word=word,
                    opened_letters=new_opened_letters,
                    attempts=attempt,
                )

            return HangmanDTO(
                state=HangmanState.letter_match,
                word=None,
                opened_letters=new_opened_letters,
                attempts=attempt,
            )

        attempt += 1
        if attempt == 6:
            return HangmanDTO(
                state=HangmanState.lose,
                word=word,
                opened_letters=word,
                attempts=attempt,
            )

        return HangmanDTO(
            state=HangmanState.no_letter_match,
            word=None,
            opened_letters=opened_letters,
            attempts=attempt,
        )

    if user_attempt == word:
        return HangmanDTO(
            state=HangmanState.win,
            word=word,
            opened_letters=opened_letters,
            attempts=attempt,
        )

    attempt += 1
    if attempt == 6:
        return HangmanDTO(
            state=HangmanState.lose,
            word=word,
            opened_letters=word,
            attempts=attempt,
        )

    return HangmanDTO(
        state=HangmanState.no_word_match,
        word=None,
        opened_letters=opened_letters,
        attempts=attempt,
    )


class HangmanService:
    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def start_game(self, chat_id, user_id, difficulty) -> HangmanDTO:
        async with self.uow:
            await self.uow.gamesession.clear_by_chat_id(chat_id=chat_id)
            if difficulty == "easy":
                word = await self.uow.hangman.get_random_easy()
            elif difficulty == "medium":
                word = await self.uow.hangman.get_random_medium()
            elif difficulty == "hard":
                word = await self.uow.hangman.get_random_hard()
            else:
                raise GameLogicError

            if word is None:
                raise GameLogicError

            attempt = 0
            opened_letters = "_" * len(word)
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
            result = HangmanDTO(
                state=None,
                word=None,
                opened_letters=opened_letters,
                attempts=attempt,
            )
            await self.uow.commit()
            logging.debug(f"Game started! Session info: {gamesession.__dict__}")
            return result

    async def check_state(self, chat_id, user_id, user_attempt) -> HangmanDTO:
        async with self.uow:
            gamesesssion = await self.uow.gamesession.get_by_chat_id(chat_id)
            if gamesesssion is None:
                logging.error("game not found")
                raise GameNotFound

            hangman_info = game_logic(
                gamesesssion.session_info, user_attempt=user_attempt
            )

            if hangman_info.state in (HangmanState.lose, HangmanState.win):
                to_history = GameHistory(
                    chat_id=chat_id,
                    user_id=user_id,
                    game_type="hangman",
                    game_result=1 if hangman_info.state == HangmanState.win else 0,
                )
                await self.uow.gamesession.clear_by_chat_id(chat_id)
                logging.debug(f" adding game to history: {to_history.__dict__}")
                await self.uow.gamehistory.add(to_history)
                logging.debug(f"{hangman_info}")
                await self.uow.commit()
                return hangman_info

            gamesesssion.session_info.update(
                {
                    "attempt": hangman_info.attempts,
                    "opened_letters": hangman_info.opened_letters,
                }
            )
            await self.uow.commit()
            logging.debug(f"checking state... Current state: {hangman_info}")
            return hangman_info
