import asyncio
import logging

from pyrogram import Client, idle
from pyrogram.types import Chat

import hurricane
from hurricane import utils
from hurricane.auth import Auth
from hurricane.database import Database
from hurricane.database.assets import AssetManager
from hurricane.dispatcher import Dispatcher
from hurricane.inline.base import InlineManager
from hurricane.modloader import ModuleLoader
from hurricane.log import TelegramLogHandler

logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logger = logging.getLogger("hurricane")

BASE_PATH = utils.get_base_path()


async def create_log_chat(client: Client, loader: ModuleLoader) -> Chat:
    return await utils.create_asset_chat(
        client,
        loader,
        "hurricane-logs",
        "Your userbot logs will be sent here",
        invite_bot=True,
    )


async def main():
    client = await Auth().authorize()

    with (BASE_PATH / "assets" / "logo.txt").open(mode="r", encoding="utf-8") as f:
        logo = f.read()
    print(logo)

    database = Database(BASE_PATH / "database.json")
    client.hurricane_database = database
    inline = InlineManager(client, database)
    t = database.get("core.inline", "token")
    await inline.load(t if t else await inline.obtain_token())

    loader = ModuleLoader(client, database, inline)
    client.loader = loader
    await loader.load()

    asset_manager = AssetManager(loader, client)
    await asset_manager.load()
    dp = Dispatcher(client, loader)
    await dp.load()

    chat = await create_log_chat(client, loader)
    logging.getLogger().addHandler(TelegramLogHandler(database, client, inline, chat))
    logger.info("Hurricane userbot is loaded.")
    load_text = (
        f"🌪 <b>Hurricane userbot {hurricane.__version__} started</b>\n"
        f'🔑 <b>Version: <a href="{hurricane.repository_url}/commit/{hurricane.commit_hex}">{hurricane.commit_hex[:7]}</a></b>'
    )

    await inline.bot.send_message(chat_id=chat.id, text=load_text)

    await idle()
    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
    print("\rGoodbye!")
