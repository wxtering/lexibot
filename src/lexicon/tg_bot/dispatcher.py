from aiogram import Dispatcher

from src.lexicon.tg_bot.routers import routers


def setup_dispatcher(dp: Dispatcher):
    for router in routers:
        dp.include_router(router)
    return dp
