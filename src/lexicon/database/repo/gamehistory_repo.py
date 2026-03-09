from sqlalchemy.ext.asyncio.session import AsyncSession

from database.models.models import GameHistory


class GameHistoryRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, game_result: GameHistory) -> None:
        self.session.add(game_result)
