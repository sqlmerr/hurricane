import asyncio
import logging

from pyrogram.raw.functions.account import DeleteAccount
from pyrogram import Client, idle
from pyrogram.types import Chat
import hurricane
from hurricane import utils
from hurricane.auth import Auth
from hurricane.database import Database
from hurricane.database.assets import AssetManager
from hurricane.dispatcher import Dispatcher
from hurricane.eventbus import EventBus
from hurricane.inline.base import InlineManager
from hurricane.modloader import ModuleLoader
from hurricane.log import TelegramLogHandler

logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logger = logging.getLogger("hurricane")

BASE_PATH = utils.get_base_path()


async def create_log_chat(client: Client, inline: InlineManager) -> Chat:
    return await utils.create_asset_chat(
        client,
        inline,
        "hurricane-logs",
        "Your userbot logs will be sent here",
        invite_bot=True,
    )


async def main():
    DeleteAccount.__new__ = None
    client = await Auth().authorize()

    with (BASE_PATH / "assets" / "logo.txt").open(mode="r", encoding="utf-8") as f:
        logo = f.read()
    print(logo)

    database = Database(BASE_PATH / "database.json")
    client.hurricane_database = database

    eventbus = EventBus()
    inline = InlineManager(client, database, eventbus)
    t = database.get("core.inline", "token")
    await inline.load(t if t else await inline.obtain_token())

    chat = await create_log_chat(client, inline)
    logging.getLogger().addHandler(TelegramLogHandler(database, client, inline, chat))

    loader = ModuleLoader(client, database, inline, eventbus)
    await loader.load()
    client.loader = loader

    asset_manager = AssetManager(loader, client)
    await asset_manager.load()
    dp = Dispatcher(client, loader)
    await dp.load()

    logger.info("Hurricane userbot is loaded.")
    load_text = (
        f"🌪 <b>Hurricane userbot {hurricane.__version__} started</b>\n"
        f'🔑 <b>Version: <a href="{hurricane.repository_url}/commit/{hurricane.commit_hex}">{hurricane.__version__} @ {hurricane.commit_hex[:7]}</a></b>'
    )

    await inline.bot.send_message(chat_id=chat.id, text=load_text)
    await eventbus.publish("full_load", None)

    await idle()
    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
    print("\rGoodbye!")
