from aiogram.utils.keyboard import InlineKeyboardBuilder
from tg_bot.callbacks.stats import (
    LeaderboardGameTypeStatsCallback,
    UserGameTypeStatsCallback,
)


def build_stats_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔍 Моя Статистика", callback_data="user_stats")
    keyboard.button(text="🔍 Таблица лидеров", callback_data="leaderboard")
    keyboard.button(text="Назад в меню", callback_data="back_to_menu")
    return keyboard.as_markup()


def user_stats_type_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔍 Статистика по виселице",
        callback_data=UserGameTypeStatsCallback(game_type="hangman"),
    )
    keyboard.button(
        text="🔍 Статистика по квизу",
        callback_data=UserGameTypeStatsCallback(game_type="quiz"),
    )
    keyboard.button(text="Назад в меню", callback_data="back_to_menu")
    return keyboard.as_markup()


def leaderboard_type_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔍 Таблица лидеров по виселице",
        callback_data=LeaderboardGameTypeStatsCallback(game_type="hangman"),
    )
    keyboard.button(
        text="🔍 Таблица лидеров по квизу",
        callback_data=LeaderboardGameTypeStatsCallback(game_type="quiz"),
    )
    keyboard.button(text="Назад в меню", callback_data="back_to_menu")
    return keyboard.as_markup()


def back_to_menu_button():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Назад в меню", callback_data="back_to_menu")
    return keyboard.as_markup()
