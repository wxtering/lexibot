from aiogram.fsm.state import State, StatesGroup


class HangmanState(StatesGroup):
    difficulty = State()
