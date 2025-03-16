from pyrogram.types import Message

import hurricane
from hurricane.addons.command import CommandAddon, simple_command, CommandContext
from hurricane.addons.translate import TranslateAddon
from hurricane.security.rules import OnlyMe


class Security(hurricane.Module):
    name = "security"
    developer = "sqlmerr"
    version = hurricane.__version__

    def __init__(self):
        self.t = TranslateAddon(
            self,
            en={
                "no_args": "<emoji id='5210952531676504517'>🚫</emoji> <b>No args!</b>",
                "no_reply": "<emoji id='5210952531676504517'>🚫</emoji> <b>No reply!</b>",
                "alredy_in_group": "<emoji id='5210952531676504517'>🚫</emoji> <b>User already in group `{}`!</b>",
                "success": "<emoji id='5260463209562776385'>✅</emoji>",
            },
            ru={
                "no_args": "<emoji id='5210952531676504517'>🚫</emoji> <b>Аргументы не переданы!</b>",
                "no_reply": "<emoji id='5210952531676504517'>🚫</emoji> <b>Вы не ответили на сообщение!</b>",
                "alredy_in_group": "<emoji id='5210952531676504517'>🚫</emoji> <b>Пользователь уже в группе `{}`!</b>",
                "success": "<emoji id='5260463209562776385'>✅</emoji>",
            },
        )

        self.c = CommandAddon(self)
        self.c.register(simple_command("addowner", self.addowner_cmd, rules=[OnlyMe()]))

    async def addowner_cmd(self, message: Message, context: CommandContext):
        """Add user to owner security group"""
        reply = message.reply_to_message
        args = context.args.split()
        if len(args) < 1 and not reply:
            await self.respond(message, self.t.no_reply())
            return

        if reply and (len(args) < 1 or not args[0].isdigit()):
            user = reply.from_user.id
        else:
            user = int(args[0])

        owners = self.db.get("core.security", "owners", [self.client.me.id])
        if user in owners:
            await self.respond(message, self.t.already_in_group())
            return
        owners.append(user)
        self.db.set("core.security", "owners", owners)

        await self.respond(message, self.t.success())
        return
