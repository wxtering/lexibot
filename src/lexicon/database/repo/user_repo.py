from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.lexicon.database.models.models import UserData


class UserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_user(self, user: UserData) -> None:
        stmt = (
            insert(UserData)
            .values(tg_id=user.tg_id, username=user.username)
            .on_conflict_do_nothing()
        )
        await self.session.execute(stmt)
