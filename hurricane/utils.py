import asyncio
import random
import string
import os

from pyrogram import Client
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import Chat, Message, MessageEntity
from pathlib import Path

from hurricane.inline.base import InlineManager


async def fw_protect():
    await asyncio.sleep(random.randint(1000, 3000) / 1000)


async def create_asset_chat(
    client: Client,
    inline: InlineManager,
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
        if invite_bot and inline.bot is not None:
            users.append((await inline.bot.me()).id)
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


async def respond(
    message: Message,
    text: str,
    parse_mode: ParseMode | None = None,
    entities: list[MessageEntity] = None,
    disable_web_page_preview: bool = None,
    show_caption_above_media: bool = None,
) -> Message:
    me = message._client.me.id
    if message.from_user.id == me:
        return await message.edit(
            text,
            parse_mode,
            entities,
            disable_web_page_preview,
            show_caption_above_media,
        )
    if hasattr(message, "hurricane_respond_new_msg"):
        msg_id = message.hurricane_respond_new_msg
        return await message._client.edit_message_text(
            message.chat.id,
            msg_id,
            text,
            parse_mode,
            entities,
            disable_web_page_preview,
            show_caption_above_media,
        )

    msg = await message.reply(
        text,
        parse_mode=parse_mode,
        entities=entities,
        disable_web_page_preview=disable_web_page_preview,
        show_caption_above_media=show_caption_above_media,
    )
    message.hurricane_respond_new_msg = msg.id
    return msg


def get_ram() -> float:
    try:
        import psutil

        process = psutil.Process(os.getpid())
        mem = process.memory_info()[0] / 2.0**20
        for child in process.children(recursive=True):
            mem += child.memory_info()[0] / 2.0**20
        return round(mem, 1)
    except:
        return 0
