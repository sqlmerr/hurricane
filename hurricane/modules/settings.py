from pyrogram.types import Message

import hurricane
from hurricane.addons.command import CommandContext, simple_command
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
            },
            ru={
                "no_args": "<emoji id='5210952531676504517'>🚫</emoji> <b>Аргументы не переданы!</b>",
                "no_lang": "<emoji id='5210952531676504517'>🚫</emoji> <b>Язык не найден!</b>",
                "set_lang_text": "<emoji id='5260463209562776385'>✅</emoji> <b>Язык успешно изменен!</b>",
            },
        )
        self.commands.register(
            simple_command(
                "lang", self.set_lang_cmd, is_global=True, aliases=["set_lang"]
            )
        )

    async def set_lang_cmd(self, message: Message, context: CommandContext) -> None:
        """Change userbot language"""

        args = context.args.split()
        if len(args) < 1:
            await message.edit(self.t("no_args"))
            return

        lang = args[0].lower().strip()
        if lang not in SUPPORTED_LANGUAGES:
            await message.edit(self.t("no_lang"))
            return

        self.set("lang", lang)
        await message.edit(self.t("set_lang_text"))
