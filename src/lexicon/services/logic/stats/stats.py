import logging

from src.lexicon.services.dto.leaderboard import (
    LeaderboardDTO,
    LeaderboardEntity,
    UserStatsDTO,
)
from src.lexicon.services.entity.uow import UnitOfWork

logging = logging.getLogger(__name__)


def get_leaderboard_stats():
    pass


class StatsService:
    uow: UnitOfWork

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_leaderboard(self, game_type: str) -> LeaderboardDTO:
        async with self.uow:
            row_leaderboard = await self.uow.stats.get_leaderboard(game_type)
            if not row_leaderboard:
                return LeaderboardDTO(has_games=False, leaders=[])
            else:
                leaderboard_list = list()
                for user in row_leaderboard:
                    username = user.get("username", "anon")
                    wins = user.get("wins", 0)
                    total = user.get("total_games", 0)
                    loses = total - wins
                    wr = int(wins / total * 100) if total else 0
                    leaderboard_list.append(
                        LeaderboardEntity(
                            username=username,
                            wins=wins,
                            loses=loses,
                            total=total,
                            wr=wr,
                        )
                    )
            return LeaderboardDTO(has_games=True, leaders=leaderboard_list)

    async def get_user_stats(self, user_id: int, game_type: str) -> UserStatsDTO:
        async with self.uow:
            user_stats = await self.uow.stats.get_user_stats(user_id, game_type)
            if not user_stats:
                return UserStatsDTO(game_type=game_type, has_games=True)

            else:
                wins = user_stats.get(True, 0)
                loses = user_stats.get(False, 0)
                total = wins + loses
                wr = int(wins / total * 100) if total else 0
                return UserStatsDTO(
                    game_type=game_type,
                    has_games=True,
                    wins=wins,
                    loses=loses,
                    total=total,
                    wr=wr,
                )


# games
# wins
# loses
