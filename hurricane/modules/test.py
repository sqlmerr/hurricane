import time

from pyrogram.types import Message

import hurricane
from hurricane.addons.command import simple_command, CommandContext
from hurricane.addons.translate import TranslateAddon


class TestMod(hurricane.Module):
    name = "test"
    developer = "@sqlmerr"
    version = hurricane.__version__

    def __init__(self):
        self.t = TranslateAddon(
            self, ru={
                "ping_txt": "🏓 <b>Понг! {}</b>"
            }, en={
                "ping_txt": "🏓 <b>Pong! {}</b>"
            }
        )

    async def on_load(self):
        self.commands.register(
            simple_command("ping", self.ping_command, is_global=True)
        )

    async def ping_command(self, message: Message, context: CommandContext) -> None:
        start = time.perf_counter()
        await message.edit(self.t("ping_txt").format(""))
        end = time.perf_counter()

        await message.edit(self.t("ping_txt").format(round(end - start, 2)))
