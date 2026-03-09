from aiogram.fsm.state import State, StatesGroup


class HangmanFsmState(StatesGroup):
    difficulty = State()
