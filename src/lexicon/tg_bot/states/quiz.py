from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    ingame = State()
