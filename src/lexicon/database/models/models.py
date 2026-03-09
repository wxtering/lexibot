from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from .base import Base


### UserData ###
class UserData(Base):
    __tablename__ = "users_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    user_games_history: Mapped[list["GameHistory"]] = relationship(
        "GameHistory", back_populates="user_data"
    )


### GameHistory ###
class GameHistory(Base):
    __tablename__ = "games_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users_data.tg_id"), nullable=False
    )
    game_type: Mapped[str] = mapped_column(nullable=False)
    game_result: Mapped[bool] = mapped_column(nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    user_data: Mapped["UserData"] = relationship(
        "UserData", back_populates="user_games_history"
    )


### GameSessions ###
class GameSessions(Base):
    __tablename__ = "game_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    game_type: Mapped[str] = mapped_column(nullable=False)
    session_info: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON), nullable=False
    )


class HangmanWords(Base):
    __tablename__ = "hangman_words"

    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(nullable=False)


class QuizQuestions(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(nullable=False)
    definition: Mapped[str] = mapped_column(nullable=False)
