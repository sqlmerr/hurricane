from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from hurricane.addons.command import CommandAddon
from hurricane.pkgloader import PackageLoader


async def message_filters(app: Client, message: Message) -> bool:
    if message.chat.id == app.me.id or message.outgoing:
        return True

    return False


class Dispatcher:
    def __init__(self, client: Client, loader: PackageLoader):
        self.client = client
        self.loader = loader

    async def _message_handler(self, app: Client, message: Message) -> None:
        if not await message_filters(app, message):
            return

        prefix = self.loader._db.get("settings", "prefix", ".")
        _, command = message.text.split(prefix, 1)

        for name, pkg in self.loader.packages.items():
            addon = [a for a in pkg.addons if isinstance(a, CommandAddon)]
            if not addon:
                continue
            addon = addon[0]
            status = await addon.handle_command(command, message)
            if status:
                break

    async def load(self) -> None:
        self.client.add_handler(MessageHandler(self._message_handler, filters.all))
