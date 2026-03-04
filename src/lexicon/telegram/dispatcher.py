from aiogram import Dispatcher
from routers import routers


def setup_dispatcher(dp: Dispatcher):
    for router in routers:
        dp.include_router(router)
    return dp
