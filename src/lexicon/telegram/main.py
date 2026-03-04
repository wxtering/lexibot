import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from configuration.cfg import get_bot_config
from dispatcher import setup_dispatcher


async def start_bot():
    config = get_bot_config()
    bot = Bot(
        token=config.bot_token.get_secret_value(), default_parse_mode=ParseMode.HTML
    )
    dp = Dispatcher(
        fsm_strategy=FSMStrategy.CHAT,
    )
    setup_dispatcher(dp)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
