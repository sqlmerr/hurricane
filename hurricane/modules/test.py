import time

from pyrogram.types import Message

import hurricane
from hurricane.addons.command import simple_command, CommandContext


class TestMod(hurricane.Module  ):
    name = "test"
    developer = "@sqlmerr"
    version = hurricane.__version__

    async def on_load(self):
        self.commands.register(
            simple_command("ping", self.ping_command, is_global=True)
        )

    async def ping_command(self, message: Message, context: CommandContext) -> None:
        start = time.perf_counter()
        await message.edit("<b>Pong!</b>")
        end = time.perf_counter()

        await message.edit(f"<b>Pong! {round(end - start, 2)}</b>")
