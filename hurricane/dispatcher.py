from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, EditedMessageHandler
from pyrogram.types import Message

from hurricane.addons.command import CommandAddon
from hurricane.modloader import ModuleLoader


async def message_filters(app: Client, message: Message) -> bool:
    if message.chat.id == app.me.id or message.outgoing:
        return True

    return False


class Dispatcher:
    def __init__(self, client: Client, loader: ModuleLoader):
        self.client = client
        self.loader = loader

    async def _message_handler(self, app: Client, message: Message) -> None:
        if not await message_filters(app, message):
            return

        prefix = self.loader._db.get("settings", "prefix", ".")
        if not message.text or (
            message.text and not message.text.lower().strip().startswith(prefix)
        ):
            return
        _, command = message.text.split(prefix, 1)

        for name, mod in self.loader.modules.items():
            addon = mod.find_addon(CommandAddon)
            if not addon:
                continue
            status = await addon.handle_command(command, message)
            if status:
                break

    async def load(self) -> None:
        self.client.add_handler(MessageHandler(self._message_handler, filters.all))
        self.client.add_handler(
            EditedMessageHandler(self._message_handler, filters.all)
        )
