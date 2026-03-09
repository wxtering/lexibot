from random import randint

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from database.models.models import HangmanWords


class HangmanRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_random_easy(self) -> str | None:
        stmt = (
            select(HangmanWords.word)
            .where(func.length(HangmanWords.word) == 5)
            .order_by(func.random())
            .limit(1)
        )
        r = await self.session.execute(stmt)
        return r.scalar_one_or_none()

    async def get_random_medium(self) -> str | None:
        stmt = (
            select(HangmanWords.word)
            .where(func.length(HangmanWords.word) == randint(6, 8))
            .order_by(func.random())
            .limit(1)
        )
        r = await self.session.execute(stmt)
        return r.scalar_one_or_none()

    async def get_random_hard(self):
        stmt = (
            select(HangmanWords.word)
            .where(func.length(HangmanWords.word) == randint(9, 14))
            .order_by(func.random())
            .limit(1)
        )
        r = await self.session.execute(stmt)
        return r.scalar_one_or_none()
