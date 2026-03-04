from aiogram.utils.keyboard import InlineKeyboardBuilder
from callbacks.hangman import HangmanStartCallback


def get_menu_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="статистика", callback_data="stats")
    keyboard.button(text="Выбор игры", callback_data="game_selection")
    keyboard.button(text="Назад в меню", callback_data="back_to_menu")
    return keyboard.as_markup()


def back_to_menu_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Назад в меню", callback_data="back_to_menu")
    return keyboard.as_markup()


def game_selection_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Виселица", callback_data="hangman_difficulty")
    keyboard.button(text="Wordle", callback_data="wordle_difficulty")
    keyboard.button(text="Назад", callback_data="back_to_menu")
    return keyboard.as_markup()


def hangman_difficulty_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Легкий", callback_data=HangmanStartCallback(difficulty="easy")
    )
    keyboard.button(
        text="Средний", callback_data=HangmanStartCallback(difficulty="medium")
    )
    keyboard.button(
        text="Сложный", callback_data=HangmanStartCallback(difficulty="hard")
    )
    keyboard.button(text="Назад в меню", callback_data="back_to_menu")
    return keyboard.as_markup()


def wordle_difficulty_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Легкий", callback_data="wordle_easy")
    keyboard.button(text="Средний", callback_data="wordle_medium")
