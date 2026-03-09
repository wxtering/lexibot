from database.models.models import GameSessions
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import delete


class GameSessionRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, gamesession: GameSessions) -> None:
        self.session.add(gamesession)

    async def get_by_chat_id(self, chat_id: int) -> GameSessions | None:
        stmt = select(GameSessions).where(GameSessions.chat_id == chat_id)
        r = await self.session.execute(stmt)
        return r.scalar_one_or_none()

    async def clear_by_chat_id(self, chat_id: int) -> None:
        stmt = delete(GameSessions).where(GameSessions.chat_id == chat_id)
        await self.session.execute(stmt)
