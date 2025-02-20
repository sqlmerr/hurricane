import asyncio
import logging
import re

from aiogram.utils.token import validate_token, TokenValidationError
from pyrogram import Client
from pyrogram.errors import YouBlockedUser

import hurricane
from hurricane.database import Database
from hurricane.utils import fw_protect


class TokenManager:
    def __init__(self, db: Database, client: Client) -> None:
        self.db = db
        self.client = client

    async def create_bot(self, username: str | None = None) -> str | None:
        if token := await self.find_token(username):
            return token
        logging.info("Creating new bot")

        async with hurricane.Conversation(self.client, "@BotFather", True) as conv:
            try:
                await conv.ask("/cancel")
            except YouBlockedUser:
                await self.client.unblock_user("@BotFather")

            await conv.get_response()

            await conv.ask("/newbot")
            response = await conv.get_response()

            if not all(
                phrase not in response.text for phrase in ["That I cannot do.", "Sorry"]
            ):
                logging.error("Error while creating bot. @BotFather 's answer:")
                logging.error(response.text)

                if "too many attempts" in response.text:
                    seconds = response.text.split()[-2]
                    logging.error(f"Please try after {seconds} seconds")

            await conv.ask(
                f"Hurricane Userbot of {self.client.me.username if self.client.me.username else self.client.me.first_name[:30]}"
            )
            await conv.get_response()

            if username is None:
                username = f"hurricane_{hurricane.utils.random_identifier(6)}_bot"

            await conv.ask(username)

            await asyncio.sleep(0.5)
            response = await conv.get_response()

            search = re.search(r"(?<=<code>)(.*?)(?=</code>)", response.text.html)
            if not search:
                logging.error("Error while creating bot. @BotFather 's answer:")
                return logging.error(response.text)

            token = search.group(0)
            self.db.set("core.inline", "username", username)
            # await conv.ask("/setuserpic")
            # await conv.get_response()

            # await conv.ask("@" + username)
            # await conv.get_response()

            # await conv.ask_media("assets/bot_avatar.png", media_type="photo")
            # await conv.get_response()

            await conv.ask("/setinline")
            await conv.get_response()

            await conv.ask("@" + username)
            await conv.get_response()

            await conv.ask("cmd >")
            await conv.get_response()

            logging.info("Bot successfully created")
            async with hurricane.Conversation(self.client, f"@{username}", True) as c:
                await conv.ask("/start")
            return token

    async def find_token(self, username: str | None = None) -> str | None:
        if token := self.db.get("core.inline", "token"):
            try:
                validate_token(token)
            except TokenValidationError:
                self.db.set("core.inline", "token", None)
                return await self.find_token()
            return token

        async with hurricane.Conversation(
            self.client, "@BotFather", purge=True
        ) as conv:
            await fw_protect()
            try:
                m = await conv.ask("/token")
                await fw_protect()
            except YouBlockedUser:
                await self.client.unblock_user("@BotFather")
                await fw_protect()
                m = await conv.ask("/token")

            r = await conv.get_response()

            if not r.reply_markup:
                return None
            for row in r.reply_markup.keyboard:
                for b in row:
                    if not username and not re.search(
                        r"@hurricane_[0-9a-zA-Z]{6}_bot", b
                    ):
                        continue
                    elif username and b.strip("@").lower() != username.lower():
                        continue

                    await fw_protect()
                    m = await conv.ask(b)
                    await fw_protect()
                    r = await conv.get_response()
                    token = r.text.splitlines()[1]
                    return token
