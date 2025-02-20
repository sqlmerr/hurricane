import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.token import TokenValidationError
from pyrogram import Client

import hurricane
from hurricane.database import Database


class InlineManager:
    def __init__(self, db: Database) -> None:
        self.db = db

        self._bot: Bot | None = None
        self._dp: Dispatcher | None = None

    @property
    def bot(self) -> Bot | None:
        return self._bot

    @property
    def dp(self) -> Dispatcher | None:
        return self._dp

    def _obtain_token(self, client: Client) -> str: ...

    async def load(self, token: str) -> None:
        try:
            self._bot = Bot(
                token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
        except TokenValidationError:
            print("Got invalid token. Bot can't be created")
            return

        self.db.set("core.inline", "token", token)
        self._dp = Dispatcher()
        await self._bot.delete_webhook(drop_pending_updates=True)

        asyncio.ensure_future(self._dp.start_polling(handle_signals=False))
