from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import CallbackQuery, Message, TelegramObject


class GroupChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            if event.chat.type == ChatType.GROUP:
                result = await handler(event, data)
                return result
        elif isinstance(event, CallbackQuery):
            if event.message.chat.type == ChatType.GROUP:
                result = await handler(event, data)
                return result
        return None
