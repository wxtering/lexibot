import logging

from src.lexicon.database.models.models import UserData
from src.lexicon.services.entity.uow import UnitOfWork

logging = logging.getLogger(__name__)


class UserService:
    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def add_user(self, username, user_id):
        async with self.uow:
            user = UserData(tg_id=user_id, username=username)
            await self.uow.userdata.add_user(user)
            await self.uow.commit()
