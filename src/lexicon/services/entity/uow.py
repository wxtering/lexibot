from typing import Self

from database.repo.gamehistory_repo import GameHistoryRepo
from database.repo.gamesession_repo import GameSessionRepo
from database.repo.hangman_repo import HangmanRepo
from database.repo.quiz_repo import QuizRepo
from database.repo.stats_repo import StatsRepo
from database.repo.user_repo import UserRepo
from database.session import DEFAULT_SESSION_FACTORY


class UnitOfWork:
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        ###
        self.gamehistory = GameHistoryRepo(self.session)
        self.gamesession = GameSessionRepo(self.session)
        self.stats = StatsRepo(self.session)
        self.userdata = UserRepo(self.session)
        self.hangman = HangmanRepo(self.session)
        self.quiz = QuizRepo(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                pass
            else:
                await self.session.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        if self.session:
            await self.session.rollback()
