import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
    CallbackQuery,
)
from aiogram.utils.token import TokenValidationError
from pyrogram import Client

from hurricane.database import Database
from .units import UnitManager
from .token import TokenManager
from .. import utils


class InlineManager(UnitManager):
    def __init__(self, client: Client, db: Database) -> None:
        super().__init__()

        self._db = db
        self._client = client
        self._token_manager = TokenManager(db, client)

        self._bot: Bot | None = None
        self.bot_id: int | None = None
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
        me = await self._bot.me()
        self.bot_id = me.id

        self._db.set("core.inline", "token", token)
        self._db.set("core.inline", "username", me.username)
        self._db.set("core.inline", "use", True)
        self._dp = Dispatcher()

        self._dp.message.register(self._message_handler)
        self._dp.inline_query.register(self._inline_query)
        self._dp.callback_query.register(self._callback_handler)

        await self._bot.delete_webhook(drop_pending_updates=True)

        asyncio.ensure_future(self._dp.start_polling(self._bot, handle_signals=False))

    async def _inline_query(self, query: InlineQuery) -> None:
        if self._client.me.id != query.from_user.id:
            await query.answer(
                [
                    InlineQueryResultArticle(
                        id=utils.random_identifier(),
                        title="Not allowed!",
                        description="mising rights",
                        input_message_content=InputTextMessageContent(
                            message_text="You are not allowed to do that."
                        ),
                    )
                ]
            )
            return

        q = query.query.split(maxsplit=1)
        if len(q) == 0:
            await query.answer(
                [
                    InlineQueryResultArticle(
                        id=utils.random_identifier(),
                        title="?",
                        input_message_content=InputTextMessageContent(
                            message_text="<b>Not found</b>"
                        ),
                    )
                ]
            )
            return

        u = q[0].split(":")
        if len(u) == 1:
            return

        uname, uid = u[0].lower(), u[1]

        for unit in self._units:
            if uname != unit.name:
                continue
            if uid != unit.uid:
                continue

            await unit.handler(query, uid)
            return

    async def _message_handler(self, message: Message) -> None:
        if (
            message.text == "/start"
            and message.chat.type == "private"
            and message.from_user.id == self._client.me.id
        ):
            await message.reply("<b>🌪 Welcome to Hurricane userbot!</b>")
            return

    async def _callback_handler(self, callback: CallbackQuery) -> None:
        if "form" in callback.data:
            s = callback.data.split(":")
            if len(s) < 3:
                return
            unit_id, _, uid = s

            for unit in self._units:
                if unit.name != "form":
                    continue
                if unit.uid != unit_id:
                    continue

                await unit.callback_handler(callback, uid)
                return
