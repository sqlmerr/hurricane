import asyncio
import logging
from types import TracebackType

from pyrogram import Client
from pyrogram.types import Message


class Conversation:
    """Диалог с пользователем. Отправка сообщений и ожидание ответа"""

    def __init__(self, app: Client, chat_id: str | int, purge: bool = False) -> None:
        self.app = app
        self.chat_id = chat_id
        self.purge = purge

        self.messages_to_purge: list[Message] = []

    async def __aenter__(self) -> "Conversation":
        return self

    async def __aexit__(
        self, exc_type: type, exc_value: Exception, exc_traceback: TracebackType
    ) -> None:
        if all([exc_type, exc_value, exc_traceback]):
            logging.exception(exc_value)
        else:
            if self.purge:
                await self._purge()

        return self.messages_to_purge.clear()

    async def ask(self, text: str, *args, **kwargs) -> Message:
        message = await self.app.send_message(self.chat_id, text, *args, **kwargs)

        self.messages_to_purge.append(message)
        return message

    async def ask_message(self, message: Message) -> Message:
        message = await message.copy(self.chat_id)

        self.messages_to_purge.append(message)
        return message

    async def get_response(self, timeout: int = 30) -> Message:
        responses = self.app.get_chat_history(self.chat_id, limit=1)
        r = None
        async for response in responses:
            if response.from_user.is_self:
                timeout -= 1
                if timeout == 0:
                    raise TimeoutError

                await asyncio.sleep(1)
                responses = self.app.get_chat_history(self.chat_id, limit=1)

        self.messages_to_purge.append(response)
        return response

    async def _purge(self) -> bool:
        for message in self.messages_to_purge:
            await message.delete()

        return True
