import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from dishka.integrations.aiogram import setup_dishka

from cfg import BotConfig
from src.lexicon.dependencies.di import container
from src.lexicon.tg_bot.dispatcher import setup_dispatcher


async def start_bot():
    bot_config = BotConfig()
    bot = Bot(
        token=bot_config.bot_token.get_secret_value(), default_parse_mode=ParseMode.HTML
    )
    dp = Dispatcher(
        fsm_strategy=FSMStrategy.CHAT,
    )
    setup_dispatcher(dp)
    setup_dishka(container=container, router=dp, auto_inject=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
