from database.models.models import UserData
from entity.uow import UnitOfWork


class UserService:
    uow: UnitOfWork

    def __init__(self, uow) -> None:
        self.uow = uow

    async def add_user(self, nickname, user_id):
        async with self.uow:
            user = UserData(tg_id=user_id, username=nickname)
            await self.uow.userdata.add_user(user)
            await self.uow.commit()
