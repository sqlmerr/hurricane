import tempfile
import inspect
import io

from pyrogram.types import Message

import hurricane
from hurricane.addons.command import CommandContext, simple_command, CommandAddon
from hurricane.addons.translate import TranslateAddon

class Loader(hurricane.Module):
    name = "loader"
    developer = "hurricane"
    version = hurricane.__version__

    async def on_load(self):
        self.t = TranslateAddon(
            self, 
            en={
                "no_args": "<emoji id='5210952531676504517'>🚫</emoji> <b>No args!</b>",
                "no_reply": "<emoji id='5210952531676504517'>🚫</emoji> <b>No reply!</b>",
                "invalid_encoding": "<emoji id='5210952531676504517'>🚫</emoji> <b>Invalid encoding!</b>",
                "loading_error": "<emoji id='5210952531676504517'>🚫</emoji> <b>Error while loading module!</b>",
                "success": "<emoji id='5260463209562776385'>✅</emoji> <b>Success!</b>",
                "mod_404": "<emoji id='5210952531676504517'>🚫</emoji> <b>Module not found!</b>",
                "showmod_txt": "<b>📦 Module</b> <code>{mod}</code>\n\n<b>Version:</b> <code>{ver}</code>\n<b>Author:</b> <code>{author}</code>"
            },
            ru={
                "no_args": "<emoji id='5210952531676504517'>🚫</emoji> <b>Нет аргументов!</b>",
                "no_reply": "<emoji id='5210952531676504517'>🚫</emoji> <b>Вы не ответили на сообщение!</b>",
                "invalid_encoding": "<emoji id='5210952531676504517'>🚫</emoji> <b>Невалидная кодировка!</b>",
                "loading_error": "<emoji id='5210952531676504517'>🚫</emoji> <b>Ошибка во время загрузки модуля!</b>",
                "success": "<emoji id='5260463209562776385'>✅</emoji> <b>Успешно!</b>",
                "mod_404": "<emoji id='5210952531676504517'>🚫</emoji> <b>Модуль не найден!</b>",
                "showmod_txt": "<b>📦 Модуль</b> <code>{mod}</code>\n\n<b>Версия:</b> <code>{ver}</code>\n<b>Автор:</b> <code>{author}</code>"
            },
        )
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
            await self.respond(message, self.t.no_reply())
            return

        temp_file = tempfile.NamedTemporaryFile("w")
        await reply.download(temp_file.name)

        try:
            with open(temp_file.name, encoding="utf-8") as f:
                source = f.read()
        except UnicodeDecodeError:
            temp_file.close()
            await self.respond(message, self.t.invalid_encoding())

        mod = await self.loader.load_third_party_module(source)
        if mod is None:
            await self.respond(message, self.t.loading_error())
        else:
            with open(f"hurricane/loaded_modules/{mod}.py", "w") as f:
                f.write(source)

            await self.respond(message, self.t.success())
        temp_file.close()

    async def unload_module(self, message: Message, context: CommandContext) -> None:
        args = context.args.split()
        if not args:
            await self.respond(message, self.t.no_args())
            return
        mod = args[0].strip().lower()

        try:
            self.loader.unload_module(mod)
            await self.respond(message, self.t.success())
        except ValueError:
            await self.respond(message, self.t.mod_404())
            return
        
    async def show_module(self, message: Message, context: CommandContext) -> None:
        args = context.args.split()
        if not args:
            await self.respond(message, self.t.no_args())
            return
        mod = args[0].strip().lower()
        
        module = self.loader.find_module(mod)
        if not module:
            await self.respond(message, self.t.mod_404())
            return
        
        sys_module = inspect.getmodule(module)
        if not module:
            await self.respond(message, self.t.mod_404())
            return
        
        file = io.BytesIO(inspect.getsource(sys_module).encode("utf-8"))
        file.name = f"{module.name}.py"
        file.seek(0)
        
        await message.delete()
        await self.client.send_document(message.chat.id, document=file, caption=self.t.showmod_txt(mod=module.name, ver=module.version, author=module.developer))
