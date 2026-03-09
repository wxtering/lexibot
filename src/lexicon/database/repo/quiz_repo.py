from sqlalchemy import func, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from database.models.models import QuizQuestions


class QuizRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_random(self):
        stmt = select(QuizQuestions).order_by(func.random()).limit(1)
        r = await self.session.execute(stmt)
        return r.scalar()
