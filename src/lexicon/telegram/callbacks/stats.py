from aiogram.filters.callback_data import CallbackData


class UserGameTypeStatsCallback(CallbackData, prefix="user_game_type_stats"):
    game_type: str


class LeaderboardGameTypeStatsCallback(
    CallbackData, prefix="leaderboard_game_type_stats"
):
    game_type: str
