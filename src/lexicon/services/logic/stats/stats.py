import logging

from src.lexicon.services.entity.uow import UnitOfWork

logging = logging.getLogger(__name__)


def get_leaderboard_stats():
    pass


class StatsService:
    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_leaderboard(self, game_type: str) -> dict:
        async with self.uow:
            row_leaderboard = await self.uow.stats.get_leaderboard(game_type)
            if not row_leaderboard:
                return {"has_games": False}
            else:
                leaderboard = list()
                for user in row_leaderboard:
                    username = user.get("username", "anon")
                    wins = user.get("wins", 0)
                    loses = user.get("loses", 0)
                    total = wins + loses
                    wr = round(wins / total * 100, 2) if total else 0
                    leaderboard.append(
                        {
                            "username": username,
                            "wr": wr,
                            "wins": wins,
                            "loses": loses,
                            "total": total,
                        }
                    )
                return {"has_games": True, "leaders": leaderboard}

    async def get_user_stats(self, user_id: int, game_type: str) -> dict:
        async with self.uow:
            user_stats = await self.uow.stats.get_user_stats(user_id, game_type)
            if not user_stats:
                return {"has_games": False}
            else:
                wins = user_stats.get(True, 0)
                loses = user_stats.get(False, 0)
                total = wins + loses
                wr = round(wins / total * 100, 2) if total else 0
                return {
                    "has_games": True,
                    "wr": wr,
                    "wins": wins,
                    "loses": loses,
                    "total": total,
                }


# games
# wins
# loses
