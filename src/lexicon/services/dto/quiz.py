from dataclasses import dataclass
from enum import Enum


class QuizState(Enum):
    win = "win"
    lose = "lose"
    continue_ = "continue"
    hint = "hint"


@dataclass
class QuizDTO:
    state: QuizState
    word: str
    opened_letters: str
    attempts: int
    definition: str
