from pyrogram.types import Message

import hurricane
from hurricane.addons.command import CommandContext, simple_command, CommandAddon
from hurricane.addons.translate import SUPPORTED_LANGUAGES, TranslateAddon


class Settings(hurricane.Module):
    name = "settings"
    developer = "sqlmerr"
    version = hurricane.__version__

    def __init__(self):
        self.t = TranslateAddon(
            self,
            en={
                "no_args": "<emoji id='5210952531676504517'>🚫</emoji> <b>No args!</b>",
                "no_lang": "<emoji id='5210952531676504517'>🚫</emoji> <b>Language not found!</b>",
                "set_lang_text": "<emoji id='5260463209562776385'>✅</emoji> <b>Language successfully changed!</b>",
                "set_prefix_text": "<emoji id='5260463209562776385'>✅</emoji> <b>Prefix successfully changed!</b>",
                "invalid_prefix": "<emoji id='5210952531676504517'>🚫</emoji> <b>Invalid prefix! Its length must be equal to 1</b>",
            },
            ru={
                "no_args": "<emoji id='5210952531676504517'>🚫</emoji> <b>Аргументы не переданы!</b>",
                "no_lang": "<emoji id='5210952531676504517'>🚫</emoji> <b>Язык не найден!</b>",
                "set_lang_text": "<emoji id='5260463209562776385'>✅</emoji> <b>Язык успешно изменен!</b>",
                "set_prefix_text": "<emoji id='5260463209562776385'>✅</emoji> <b>Префикс успешно изменен!</b>",
                "invalid_prefix": "<emoji id='5210952531676504517'>🚫</emoji> <b>Невалидный префикс! Его длина должна быть равна 1</b>",
            },
        )

        self.c = CommandAddon(self)
        self.c.register(
            simple_command(
                "lang",
                self.set_lang_cmd,
                is_global=True,
                aliases=["set_lang", "setlang"],
            ),
            simple_command(
                "prefix",
                self.set_prefix_cmd,
                is_global=True,
                aliases=["set_prefix", "setprefix"],
            ),
        )

    async def set_lang_cmd(self, message: Message, context: CommandContext) -> None:
        """Change userbot language"""

        args = context.args.split()
        if len(args) < 1:
            await self.respond(message, self.t("no_args"))
            return

        lang = args[0].lower().strip()
        if lang not in SUPPORTED_LANGUAGES:
            await self.respond(message, self.t("no_lang"))
            return

        self.set("lang", lang)
        await self.respond(message, self.t("set_lang_text"))

    async def set_prefix_cmd(self, message: Message, context: CommandContext) -> None:
        """Change userbot prefix"""
        args = context.args.split()
        if len(args) < 1:
            await self.respond(message, self.t.no_args())
            return

        prefix = args[0].lower().strip()
        if len(prefix) != 1:
            await self.respond(message, self.t("invalid_prefix"))
            return

        self.set("prefix", prefix)
        await self.respond(message, self.t("set_prefix_text"))
