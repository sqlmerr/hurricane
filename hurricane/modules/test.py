import time

from aiogram.types import CallbackQuery, CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pyrogram.types import Message

import hurricane
from hurricane.addons.command import simple_command, CommandContext
from hurricane.addons.inline.components import Text, UrlButton, ClickableButton, Builder
from hurricane.addons.inline.form import FormAddon
from hurricane.addons.translate import TranslateAddon
from hurricane.inline.custom import HurricaneCallbackQuery
from hurricane.types import ReplyMarkup

async def on_click(call: HurricaneCallbackQuery):
    await call.answer("arbuz")

Menu = [
    Text("test text 123"),
    UrlButton("url", "https://example.com"),
    ClickableButton("click", on_click),
]


class TestMod(hurricane.Module):
    name = "test"
    developer = "@sqlmerr"
    version = hurricane.__version__

    def __init__(self):
        self.t = TranslateAddon(
            self,
            ru={"ping_txt": "🏓 <b>Понг! {}</b>"},
            en={"ping_txt": "🏓 <b>Pong! {}</b>"},
        )

        self.commands.register(
            simple_command("ping", self.ping_command, is_global=True),
            simple_command("crash", self.crash_cmd),
            simple_command("inline", self.inline_menu_cmd),
        )

        self.form = FormAddon(self)

    async def inline_menu_cmd(self, message: Message, context: CommandContext):
        b = Builder(Menu)
        await b.build(message, self.form)

    async def inline_callback(self, call: HurricaneCallbackQuery):
        await call.answer("Hello", show_alert=True)

        b = InlineKeyboardBuilder()
        b.button(text="arbuz", copy_text=CopyTextButton(text="arbuzz"))

        await call.edit("Hiii", b.as_markup())

    async def crash_cmd(self, _, __) -> None:
        result = 1 / 0

    async def ping_command(self, message: Message, context: CommandContext) -> None:
        start = time.perf_counter()
        await message.edit(self.t.ping_txt(""))
        end = time.perf_counter()
        await message.edit(self.t.ping_txt(round(end - start / 10**6, 3)))
