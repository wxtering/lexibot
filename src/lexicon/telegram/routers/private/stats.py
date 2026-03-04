import keyboards.profile_keyboard as pkb
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from custom_callbacks.stats_callbacks import (
    LeaderboardGameTypeStatsCallback,
    UserGameTypeStatsCallback,
)
from database.repos.stats_repo import get_leaderboard_stats, get_user_stats
from middlewares.add_user_middleware import AddUserMiddleware

router = Router()
router.message.middleware(AddUserMiddleware())
router.callback_query.middleware(AddUserMiddleware())


@router.callback_query(F.data == "stats")
async def profile_stats(callback: CallbackQuery):
    await callback.message.edit_text(
        text="📊 Выберите тип статистики", reply_markup=pkb.build_stats_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "user_stats")
async def user_stats(callback: CallbackQuery):
    await callback.message.edit_text(
        text="📈 Выберите игру для просмотра статистики",
        reply_markup=pkb.user_stats_type_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "leaderboard")
async def leaderboard(callback: CallbackQuery):
    await callback.message.edit_text(
        text="🏆 Выберите игру для просмотра таблицы лидеров",
        reply_markup=pkb.leaderboard_type_keyboard(),
    )
    await callback.answer()


@router.callback_query(UserGameTypeStatsCallback.filter())
async def user_hangman_stats(
    callback: CallbackQuery, callback_data: UserGameTypeStatsCallback
):
    wins, total_games, winrate = await get_user_stats(
        callback.from_user.id, callback_data.game_type
    )
    await callback.message.edit_text(
        text=f"📈 Статистика: {callback_data.game_type}\n\n"
        f"Всего игр: {total_games}\n"
        f"Побед: {wins}\n"
        f"Процент побед: {int(winrate)}%",
        reply_markup=pkb.back_to_menu_button(),
    )
    await callback.answer()


@router.callback_query(LeaderboardGameTypeStatsCallback.filter())
async def leaderboard_hangman_stats(
    callback: CallbackQuery, callback_data: LeaderboardGameTypeStatsCallback
):
    leaderboard = await get_leaderboard_stats(callback_data.game_type)
    if callback_data.game_type != "quiz":
        leaderboard_output = "\n".join(
            [
                f"{leader[0]} - wins: {leader[1]} - total games: {leader[2]} wr: {int(leader[1] / leader[2] * 100)}%"
                for leader in leaderboard
            ]
        )
    else:
        leaderboard_output = "\n".join(
            [f"{leader[0]} - wins: {leader[1]}" for leader in leaderboard]
        )
    await callback.message.edit_text(
        text=f"🔍 Таблица лидеров по выбранной игре: {callback_data.game_type}\n"
        f"{leaderboard_output}",
        reply_markup=pkb.back_to_menu_button(),
    )
    await callback.answer()
