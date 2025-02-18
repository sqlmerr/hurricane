import tempfile

from pyrogram.types import Message

import hurricane
from hurricane.addons.command import CommandContext, simple_command


class Loader(hurricane.Module):
    name = "loader"
    developer = "@sqlmerr"
    version = hurricane.__version__

    async def on_load(self):
        self.commands.register(
            simple_command("loadmod", self.load_module, is_global=True, aliases=["lm"]),
            simple_command("unloadmod", self.unload_module, is_global=True, aliases=["ulm"]),
        )


    async def load_module(self, message: Message, context: CommandContext) -> None:
        reply = message.reply_to_message
        if not reply or (reply and reply.document is None):
            await message.edit("<b>No reply!</b>")
            return

        temp_file = tempfile.NamedTemporaryFile("w")
        await reply.download(temp_file.name)

        try:
            with open(temp_file.name, encoding="utf-8") as f:
                source = f.read()
        except UnicodeDecodeError:
            temp_file.close()
            await message.edit("<b>Invalid encoding!</b>")

        mod = await self.loader.load_third_party_module(source)
        if mod is None:
            await message.edit("<b>Error while loading module!</b>")
        else:
            with open(f"hurricane/loaded_modules/{mod}.py", "w") as f:
                f.write(source)

            await message.edit("<b>Success!</b>")
        temp_file.close()

    async def unload_module(self, message: Message, context: CommandContext) -> None:
        args = context.args.split()
        if not args:
            await message.edit("<b>No arguments!</b>")
            return
        mod = args[0].strip().lower()

        try:
            self.loader.unload_module(mod)
            await message.edit("<b>Success!</b>")
        except ValueError:
            await message.edit("<b>Module not found!</b>")
            return
