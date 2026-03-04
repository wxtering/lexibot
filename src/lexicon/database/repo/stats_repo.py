from database.models.models import GameHistory
from database.session import AsyncSession
from sqlalchemy.dialects.sqlite import insert


class StatsRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_game_result(self, game_result: GameHistory) -> None:
        stmt = (
            insert(GameHistory)
            .values(
                user_id=game_result.user_id,
                username=game_result.chat_id,
                created_at=game_result.created_at,
                game_result=game_result.game_result,
                game_type=game_result.game_type,
            )
            .on_conflict_do_nothing()
        )
        await self.session.execute(stmt)
