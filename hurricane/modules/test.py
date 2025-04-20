import atexit
import os
import sys
import time

from pyrogram.types import Message

import hurricane
from hurricane import utils
from hurricane.addons.command import simple_command, CommandContext, CommandAddon
from hurricane.addons.inline.components import (
    Text,
    ClickableButton,
    Builder,
    Group,
    RawButton,
)
from hurricane.addons.inline.form import FormAddon
from hurricane.addons.inline.menu import BaseMenu
from hurricane.addons.translate import TranslateAddon
from hurricane.inline.custom import HurricaneCallbackQuery
from hurricane.security.rules import In

from aiogram.types import Message as BotMessage


class TestMenu(BaseMenu):
    def __init__(self, form: FormAddon, count: int = 0):
        super().__init__(form, rules=[In(1341947575)])
        self.count = count

    async def increment(self, call: HurricaneCallbackQuery):
        self.count += 1
        await call.answer()
        await self.restart(self.render, call)

    async def decrement(self, call: HurricaneCallbackQuery):
        self.count -= 1
        await call.answer()
        await self.restart(self.render, call)

    def render(self) -> Builder:
        return Builder(
            Text(f"Current count: <code>{self.count}</code>"),
            Group(
                ClickableButton("+", self.increment),
                ClickableButton("-", self.decrement),
                width=2,
            ),
            RawButton({"text": "Close", "action": "close"}),
        )


class TestMod(hurricane.Module):
    name = "test"
    developer = "hurricane"
    version = hurricane.__version__

    def __init__(self):
        self.t = TranslateAddon(
            self,
            ru={
                "ping_txt": "🏓 <b>Понг! {}</b>",
                "restart_txt": "🔄 <b>Hurricane перезагружается...</b>",
                "restarted": "✅ <b>Юзербот успешно перезагрузился за {} секунд</b>",
                "loading": "✅ <b>Юзербот перезагрузился, но модули еще загружаются</b>",
            },
            en={
                "ping_txt": "🏓 <b>Pong! {}</b>",
                "restart_txt": "🔄 <b>Hurricane is restarting...</b>",
                "restarted": "✅ <b>Userbot successfully restarted in {} seconds</b>",
                "loading": "✅ <b>Userbot restarted, but modules are currently loading</b>",
            },
        )

        self.c = CommandAddon(self)
        self.c.register(
            simple_command("ping", self.ping_command, is_global=True),
            simple_command("crash", self.crash_cmd),
            simple_command("inline", self.inline_menu_cmd),
            simple_command("restart", self.restart_cmd, is_global=True),
        )

        self.form = FormAddon(self)
        self.loader.eventbus.subscribe("full_load", self.full_load_handler)
        self.loader.eventbus.subscribe("message", self.example_watcher)
        self.loader.eventbus.subscribe("inline:message", self.inline_bot_command)

    async def example_watcher(self, message: Message, data: dict):
        if message.text != "testMessage":
            return False
        print("got testMessage!")

        return True

    async def inline_bot_command(self, message: BotMessage, data: dict):
        if message.text != "/testmenu":
            return False
        await message.answer(f"<b>Hello, {message.from_user.first_name}!</b>")

        return True

    async def full_load_handler(self):
        if msg_id := self.db.get("core.start", "message_id"):
            chat_id = self.db.get("core.start", "chat_id")
            start = self.db.get("core.start", "restarted_at")
            end = time.perf_counter()
            await self.client.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=self.t.restarted(round(end - start, 2)),
            )

            self.db.set("core.start", "message_id", None)
            self.db.set("core.start", "restarted_at", None)

    async def on_load(self):
        if msg_id := self.db.get("core.start", "message_id"):
            chat_id = self.db.get("core.start", "chat_id")
            await self.client.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=self.t.loading(),
            )

    async def inline_menu_cmd(self, message: Message, context: CommandContext):
        menu = TestMenu(self.form)
        await menu.start(menu.render, message)

    async def crash_cmd(self, _, __) -> None:
        raise ValueError("test message")

    async def ping_command(self, message: Message, context: CommandContext) -> None:
        start = time.perf_counter_ns()
        await utils.respond(message, self.t.ping_txt(""))
        end = time.perf_counter_ns()
        await utils.respond(message, self.t.ping_txt(round((end - start) / 10**6, 3)))

    async def restart_cmd(self, message: Message, context: CommandContext) -> None:
        def restart():
            os.execl(sys.executable, sys.executable, "-m", "hurricane")

        await utils.respond(message, self.t.restart_txt())
        if message.from_user.id == self.client.me.id:
            self.db.set("core.start", "message_id", message.id)
            self.db.set("core.start", "chat_id", message.chat.id)
            self.db.set("core.start", "restarted_at", time.perf_counter())
        await self.loader.eventbus.publish("restart", None)
        atexit.register(restart)

        return sys.exit(0)
