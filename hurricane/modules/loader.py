import tempfile
import inspect
import io

from pyrogram.types import Message

import hurricane
from hurricane.addons.command import CommandContext, simple_command, CommandAddon


class Loader(hurricane.Module):
    name = "loader"
    developer = "@sqlmerr"
    version = hurricane.__version__

    async def on_load(self):
        self.c = CommandAddon(self)
        self.c.register(
            simple_command("loadmod", self.load_module, is_global=True, aliases=["lm"]),
            simple_command(
                "unloadmod", self.unload_module, is_global=True, aliases=["ulm"]
            ),
            simple_command("showmod", self.show_module, is_global=True, aliases=["sm", "ml"])
        )

    async def load_module(self, message: Message, context: CommandContext) -> None:
        reply = message.reply_to_message
        if not reply or (reply and reply.document is None):
            await self.respond(message, "<b>No reply!</b>")
            return

        temp_file = tempfile.NamedTemporaryFile("w")
        await reply.download(temp_file.name)

        try:
            with open(temp_file.name, encoding="utf-8") as f:
                source = f.read()
        except UnicodeDecodeError:
            temp_file.close()
            await self.respond(message, "<b>Invalid encoding!</b>")

        mod = await self.loader.load_third_party_module(source)
        if mod is None:
            await self.respond(message, "<b>Error while loading module!</b>")
        else:
            with open(f"hurricane/loaded_modules/{mod}.py", "w") as f:
                f.write(source)

            await self.respond(message, "<b>Success!</b>")
        temp_file.close()

    async def unload_module(self, message: Message, context: CommandContext) -> None:
        args = context.args.split()
        if not args:
            await self.respond(message, "<b>No arguments!</b>")
            return
        mod = args[0].strip().lower()

        try:
            self.loader.unload_module(mod)
            await self.respond(message, "<b>Success!</b>")
        except ValueError:
            await self.respond(message, "<b>Module not found!</b>")
            return
        
    async def show_module(self, message: Message, context: CommandContext) -> None:
        args = context.args.split()
        if not args:
            await self.respond(message, "<b>No arguments!</b>")
            return
        mod = args[0].strip().lower()
        
        module = self.loader.find_module(mod)
        if not module:
            await self.respond(message, "<b>Module not found!</b>")
            return
        
        sys_module = inspect.getmodule(module)
        if not module:
            await self.respond(message, "<b>Module not found!</b>")
            return
        
        file = io.BytesIO(inspect.getsource(sys_module).encode("utf-8"))
        file.name = f"{module.name}.py"
        file.seek(0)
        
        await message.delete()
        await self.client.send_document(message.chat.id, f"<b>Module {module.name}</b>", document=file)

