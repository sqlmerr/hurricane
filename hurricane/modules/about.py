import hurricane

from hurricane import utils
from hurricane.addons.command import CommandContext, simple_command, CommandAddon
from hurricane.addons.translate import TranslateAddon

from pyrogram.types import Message


class AboutMod(hurricane.Module):
    name = "about"
    version = hurricane.__version__
    developer = "hurricane"

    def __init__(self):
        self.t = TranslateAddon(
            self,
            en={
                "txt": (
                    "<emoji id='5220181540222291016'>🌪</emoji> <b>Hurricane userbot</b>\n\n"
                    "<emoji id='5305265301917549162'>📎</emoji> <b>Version</b> - <code>{version} @ {commit}</code>\n"
                    "<emoji id='5438496463044752972'>⭐️</emoji> <b>Branch</b> - <code>{branch}</code>\n\n"
                    "<emoji id='5424972470023104089'>🔥</emoji> <b>Uptime</b> - {uptime}\n"
                    "<emoji id='5341715473882955310'>⚙️</emoji> <b>Ram usage</b> - {ram}"
                )
            },
            ru={
                "txt": (
                    "<emoji id='5220181540222291016'>🌪</emoji> <b>Hurricane userbot</b>\n\n"
                    "<emoji id='5305265301917549162'>📎</emoji> <b>Версия</b> - <code>{version} @ {commit}</code>\n"
                    "<emoji id='5438496463044752972'>⭐️</emoji> <b>Ветка</b> - <code>{branch}</code>\n\n"
                    "<emoji id='5424972470023104089'>🔥</emoji> <b>Аптайм</b> - {uptime}\n"
                    "<emoji id='5341715473882955310'>⚙️</emoji> <b>Использование ram</b> - {ram}"
                )
            },
        )

        self.c = CommandAddon(self)
        self.c.register(
            simple_command("about", self.about, is_global=True, aliases=["info"])
        )

    async def about(self, message: Message, context: CommandContext):
        data = {
            "version": hurricane.__version__,
            "commit": f"<a href='{hurricane.repository_url}/commit/{hurricane.commit_hex}'>{hurricane.commit_hex[:7]}</a>",
            "branch": hurricane.repo.active_branch,
            "uptime": "...",
            "ram": "...",
        }

        text = self.t.txt(**data)
        await utils.respond(message, text)
