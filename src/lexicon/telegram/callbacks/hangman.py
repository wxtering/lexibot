from aiogram.filters.callback_data import CallbackData


class HangmanStartCallback(CallbackData, prefix="hangman"):
    difficulty: str
