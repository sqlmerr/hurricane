import asyncio
import random
import string
import os

from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import Chat
from pathlib import Path

import hurricane.modloader


async def fw_protect():
    await asyncio.sleep(random.randint(1000, 3000) / 1000)


async def create_asset_chat(
    client: Client,
    loader: "hurricane.modloader.ModuleLoader",
    title: str,
    desc: str = "",
    supergroup: bool = False,
    invite_bot: bool = False,
    archive: bool = False,
    avatar: str | None = None,
) -> Chat:
    async for dialog in client.get_dialogs():
        if dialog.chat.title == title and dialog.chat.type == (
            ChatType.SUPERGROUP if supergroup else ChatType.GROUP
        ):
            return dialog.chat

    await fw_protect()
    if supergroup:
        chat = await client.create_supergroup(title=title)
        if desc:
            await chat.set_description(desc)
    else:
        users = []
        if invite_bot and loader.inline.bot is not None:
            users.append((await loader.inline.bot.me()).id)
        chat = await client.create_group(title, users)

        if desc:
            await chat.set_description(desc)

    if archive:
        await fw_protect()
        await chat.archive()

    if avatar:
        await fw_protect()
        await client.set_chat_photo(chat.id, photo=avatar)

    return chat


def random_identifier(size: int = 10) -> str:
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(size)
    )


def get_base_path() -> Path:
    return Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
