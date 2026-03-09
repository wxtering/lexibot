from dataclasses import dataclass
from enum import Enum


class QuizState(Enum):
    win = "win"
    lose = "lose"
    continue_ = "continue"
    hint = "hint"


@dataclass
class QuizDTO:
    state: QuizState | None
    word: str | None
    opened_letters: str
    attempts: int
