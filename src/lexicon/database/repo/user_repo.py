from sqlalchemy.dialects.sqlite import insert

from database.models.models import UserData
from database.session import AsyncSession


class UserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_user(self, user: UserData) -> None:
        stmt = (
            insert(UserData)
            .values(
                tg_id=user.tg_id, username=user.username, created_at=user.created_at
            )
            .on_conflict_do_nothing()
        )
        await self.session.execute(stmt)
