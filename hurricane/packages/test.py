from pyrogram.types import Message

import hurricane
from hurricane.addons.command import simple_command, CommandContext


class TestPackage(hurricane.Package):
    name = "tester"
    developer = "@sqlmerr"
    version = hurricane.__version__

    async def on_load(self):
        # self.set("test", True)
        self.commands.register(
            simple_command("ping", self.ping_command, is_global=True)
        )

    async def ping_command(self, message: Message, context: CommandContext) -> None:
        await message.edit(f"{context.command.cmd}, {context.args}")
