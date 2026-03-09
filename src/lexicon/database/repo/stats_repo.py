from database.models.models import GameHistory, UserData
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio.session import AsyncSession


class StatsRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_stats(self, user_id: int, game_type: str) -> dict:
        stmt = (
            select(
                GameHistory.game_result,
                func.count(GameHistory.game_result),
            )
            .where(GameHistory.user_id == user_id, GameHistory.game_type == game_type)
            .group_by(GameHistory.game_result)
        )
        result = await self.session.execute(stmt)
        in_dict = {res: value for res, value in result.all()}

        return in_dict

    async def get_leaderboard(self, game_type: str) -> list:
        wins = func.sum(case((GameHistory.game_result.is_(True), 1), else_=0)).label(
            "wins"
        )
        total_games = func.count(GameHistory.id).label("total_games")
        stmt = (
            select(UserData.username, wins, total_games)
            .join(GameHistory, UserData.tg_id == GameHistory.user_id)
            .filter(GameHistory.game_type == game_type)
            .group_by(UserData.tg_id, UserData.username)
            .order_by(wins.desc())
            .limit(10)
        )
        result = await self.session.execute(stmt)
        result = result.all()
        in_dict = [row._asdict() for row in result]
        return in_dict
