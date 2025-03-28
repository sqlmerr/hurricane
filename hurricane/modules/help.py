import html

from pyrogram.types import Message

import hurricane
from hurricane import utils
from hurricane.addons.command import CommandContext, simple_command, CommandAddon
from hurricane.addons.translate import TranslateAddon


class Help(hurricane.Module):
    name = "help"
    developer = "hurricane"
    version = hurricane.__version__

    def __init__(self):
        self.t = TranslateAddon(
            self,
            en={
                "footer": "🌪 <b><i>Help</i></b>",
                "content": "<blockquote expandable>{}</blockquote>",
                "404": "<emoji id='5210952531676504517'>🚫</emoji> <b>Module not found!</b>",
                "single": (
                    "<emoji id='6030474915008745842'>📦</emoji> <b>{mod} {version}</b>\n"
                    "<emoji id='6030801830739448093'>⚠️</emoji> <i>{doc}</i>\n"
                    "{commands}\n\n"
                    "<b><i>By</i></b> <code>{developer}</code>"
                ),
            },
            ru={
                "footer": "🌪 <b><i>Помощь</i></b>",
                "content": "<blockquote expandable>{}</blockquote>",
                "404": "<emoji id='5210952531676504517'>🚫</emoji> <b>Модуль не найден!</b>",
                "single": (
                    "<emoji id='6030474915008745842'>📦</emoji> <b>{mod} {version}</b>\n"
                    "<emoji id='6030801830739448093'>⚠️</emoji> <i>{doc}</i>\n"
                    "{commands}\n\n"
                    "<b><i>By</i></b> <code>{developer}</code>"
                ),
            },
        )
        self.c = CommandAddon(self)
        self.c.register(simple_command("help", self.help_cmd, is_global=True))

    def help_menu(self, modules: dict[str, hurricane.Module]) -> str:
        content = []
        for n, m in modules.items():
            if not (command_addon := m.find_addon(CommandAddon)):
                continue
            commands = " | ".join(
                f"{'🌐' if c.is_global else ''} {k}"
                for k, c in command_addon.commands.items()
            )
            content.append(f"🔸 <code>{n}</code> ({commands})")
        content = "\n".join(content)

        text = f"{self.t('footer')}\n\n{self.t('content').format(content)}"
        return text

    async def help_cmd(self, message: Message, context: CommandContext) -> None:
        args = context.args.split()
        if len(args) < 1:
            modules = self.loader.modules
            text = self.help_menu(modules)

            await utils.respond(message, text)
            return
        mod = args[0]
        module = self.loader.find_module(mod)
        if module is None:
            await utils.respond(message, self.t("404"))
            return
        addon = module.find_addon(CommandAddon)
        if addon is None:
            await utils.respond(message, self.t("404"))
            return
        commands = list(addon.commands.values())
        c = []
        for cmd in commands:
            aliases = ", ".join(cmd.aliases)
            doc = cmd.doc
            glob = (
                " <emoji id='5870718740236079262'>🌐</emoji>" if cmd.is_global else ""
            )
            if doc is not None:
                c.append(
                    f"▪️ <code>{cmd.cmd}</code> [{aliases}]{glob} - <i>{html.escape(doc)}</i>"
                )
            else:
                c.append(f"▪️ <code>{cmd.cmd}</code> [{aliases}]{glob}")
        cmds = "\n".join(c)
        text = self.t("single").format(
            mod=mod,
            version=module.version,
            doc=module.__doc__,
            commands=cmds,
            developer=module.developer,
        )
        await utils.respond(message, text)
