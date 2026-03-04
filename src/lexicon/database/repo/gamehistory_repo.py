from database.models.models import GameHistory
from database.session import AsyncSession


class GameHistoryRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, game_result: GameHistory) -> None:
        self.session.add(game_result)
