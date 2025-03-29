import asyncio
import logging
import traceback

from pyrogram import Client
from pyrogram.types import Chat

from hurricane.database import Database
from hurricane.inline.base import InlineManager


class TelegramLogHandler(logging.Handler):
    def __init__(self, db: Database, client: Client, inline: InlineManager, chat: Chat):
        self._client = client
        self._chat = chat
        self._db = db
        self._inline = inline
        self.buffer: list[logging.LogRecord] = []
        asyncio.get_event_loop().create_task(self.send_to_tg())
        super().__init__()

    async def send_to_tg(self):
        while True:
            await asyncio.sleep(3)
            if not self.buffer:
                continue

            queue = ""
            for r in self.buffer:
                if r.exc_info:
                    exc = r.exc_info[1]
                    trace = traceback.format_exception(exc)
                    full_traceback = "\n".join(trace)
                    txt = f"<b>❌ An unexpected error recieved:</b>\n<blockquote expandable>{full_traceback}</blockquote>"
                    await self._inline.bot.send_message(self._chat.id, txt)
                else:
                    queue += f"<b>[{r.levelname}]</b>: <code>{r.message}</code>\n"

            self.buffer.clear()
            if queue:
                await self._inline.bot.send_message(self._chat.id, queue)

    def emit(self, record: logging.LogRecord) -> None:
        if not self._db.get("core.inline", "use", False):
            return
        self.buffer.append(record)
