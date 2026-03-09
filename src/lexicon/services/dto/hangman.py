from dataclasses import dataclass
from enum import Enum


class HangmanState(Enum):
    win = "win"
    lose = "lose"
    already_opened = "already_opened"
    no_word_match = "no_word_match"
    no_letter_match = "no_letter_match"
    letter_match = "letter_match"


@dataclass
class HangmanDTO:
    state: HangmanState | None
    word: str | None
    opened_letters: str
    attempts: int
