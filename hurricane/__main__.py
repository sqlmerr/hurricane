import asyncio
import logging
import os
from pathlib import Path

from pyrogram import Client, idle, filters

from hurricane.auth import Auth
from hurricane.database import Database
from hurricane.dispatcher import Dispatcher
from hurricane.modloader import ModuleLoader

logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logger = logging.getLogger("hurricane")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_PATH = Path(BASE_DIR)


async def main():
    client = await Auth().authorize()

    with (BASE_PATH / "assets" / "logo.txt").open(mode="r", encoding="utf-8") as f:
        logo = f.read()
    print(logo)

    database = Database(BASE_PATH / "database.json")
    loader = ModuleLoader(client, database)
    await loader.load()

    dp = Dispatcher(client, loader)
    await dp.load()

    await idle()
    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
    print("\rGoodbye!")
