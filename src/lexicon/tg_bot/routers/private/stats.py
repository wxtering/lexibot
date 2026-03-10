import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from dishka.integrations.aiogram import FromDishka

import src.lexicon.tg_bot.keyboards.profile_keyboard as pkb
from src.lexicon.services.dto.leaderboard import LeaderboardDTO, LeaderboardEntity
from src.lexicon.services.logic.stats.stats import StatsService
from src.lexicon.tg_bot.callbacks.stats import (
    LeaderboardGameTypeStatsCallback,
    UserGameTypeStatsCallback,
)
from src.lexicon.tg_bot.middlewares.private import PrivateChatMiddleware

logging = logging.getLogger(__name__)
router = Router()
router.message.middleware(PrivateChatMiddleware())
router.callback_query.middleware(PrivateChatMiddleware())


@router.callback_query(F.data == "stats")
async def profile(callback: CallbackQuery):
    await callback.message.edit_text(
        text="📊 Выберите тип статистики", reply_markup=pkb.build_stats_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "user_stats")
async def user_stats_gameselector(callback: CallbackQuery):
    await callback.message.edit_text(
        text="📈 Выберите игру для просмотра статистики",
        reply_markup=pkb.user_stats_type_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "leaderboard")
async def leaderboard_gameselector(callback: CallbackQuery):
    await callback.message.edit_text(
        text="🏆 Выберите игру для просмотра таблицы лидеров",
        reply_markup=pkb.leaderboard_type_keyboard(),
    )
    await callback.answer()


@router.callback_query(
    UserGameTypeStatsCallback.filter(),
)
async def user_stats(
    callback: CallbackQuery,
    callback_data: UserGameTypeStatsCallback,
    StatsService: FromDishka[StatsService],
):
    user_stats = await StatsService.get_user_stats(
        callback.from_user.id, callback_data.game_type
    )
    if not user_stats.has_games:
        await callback.message.edit_text(
            text="📊 У вас пока нет игр в этой категории",
            reply_markup=pkb.back_to_menu_button(),
        )
        await callback.answer()
    else:
        await callback.message.edit_text(
            text=f"📈 Статистика: {callback_data.game_type}\n\n"
            f"Всего игр: {user_stats.total}\n"
            f"Побед: {user_stats.wins}\n"
            f"Поражений {user_stats.loses}\n"
            f"Процент побед: {(user_stats.wr)}%",
            reply_markup=pkb.back_to_menu_button(),
        )
        await callback.answer()


@router.callback_query(LeaderboardGameTypeStatsCallback.filter())
async def leaderboard_stats(
    callback: CallbackQuery,
    callback_data: LeaderboardGameTypeStatsCallback,
    StatsService: FromDishka[StatsService],
):
    leaderboard = await StatsService.get_leaderboard(callback_data.game_type)
    if not leaderboard.has_games:
        await callback.message.edit_text(
            text="📊 Пока нет игр в этой категории",
            reply_markup=pkb.back_to_menu_button(),
        )
        await callback.answer()
        return
    else:
        leaderboard_output = "\n".join(
            [
                f"{leader.username}\n wins: {leader.wins}\n loses: {leader.loses}\n total games: {leader.total}\n wr: {leader.wr}%"
                for leader in leaderboard.leaders
            ]
        )
        await callback.message.edit_text(
            text=f"🔍 Таблица лидеров по выбранной игре: {callback_data.game_type}\n"
            f"{leaderboard_output}",
            reply_markup=pkb.back_to_menu_button(),
        )
    await callback.answer()
