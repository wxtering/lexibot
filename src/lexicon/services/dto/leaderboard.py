from dataclasses import dataclass
from enum import Enum


class HangmanStates(Enum):
    win = "win"
    lose = "lose"
    continue_ = "continue"
    hint = "hint"


@dataclass
class HangmanDTO:
    state: HangmanStates
    word: str
    opened_letters: str
    attempts: int
