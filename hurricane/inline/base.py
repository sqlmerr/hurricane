import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.token import TokenValidationError
from pyrogram import Client

from hurricane.database import Database
from hurricane.inline.token import TokenManager


class InlineManager:
    def __init__(self, client: Client, db: Database) -> None:
        self._db = db
        self._token_manager = TokenManager(db, client)

        self._bot: Bot | None = None
        self._dp: Dispatcher | None = None

    @property
    def bot(self) -> Bot | None:
        return self._bot

    @property
    def dp(self) -> Dispatcher | None:
        return self._dp

    async def obtain_token(self) -> str:
        return await self._token_manager.create_bot(
            self._db.get("core.inline", "username", None)
        )

    async def load(self, token: str) -> None:
        try:
            self._bot = Bot(
                token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
        except TokenValidationError:
            print("Got invalid token. Bot can't be created")
            return

        self._db.set("core.inline", "token", token)
        self._db.set("core.inline", "username", (await self._bot.me()).username)
        self._db.set("core.inline", "use", True)
        self._dp = Dispatcher()
        await self._bot.delete_webhook(drop_pending_updates=True)

        asyncio.ensure_future(self._dp.start_polling(self._bot, handle_signals=False))
