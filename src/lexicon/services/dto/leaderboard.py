from dataclasses import dataclass


@dataclass
class UserStatsDTO:
    game_type: str
    has_games: bool
    total: int | None = None
    wins: int | None = None
    loses: int | None = None
    wr: int | None = None


@dataclass
class LeaderboardEntity:
    username: str
    total: int
    wins: int
    loses: int
    wr: int


@dataclass
class LeaderboardDTO:
    has_games: bool
    leaders: list[LeaderboardEntity]
