from typing import Awaitable, Callable

from pyrogram.types import Message, User

from hurricane.addons.inline.components import Builder
from hurricane.addons.inline.form import FormAddon
from hurricane.inline.custom import HurricaneCallbackQuery
from hurricane.security.rules import BaseRule


class BaseMenu:
    def __init__(self, form: FormAddon, *, rules: list[BaseRule] | None = None):
        self.form = form
        self.rules = rules
        self.unit_id: str | None = None

    async def start(self, entrypoint: Callable[[], Builder], message: Message) -> None:
        builder = entrypoint()
        self.unit_id = await builder.build(message, self.form, rules=self.rules)

    async def restart(self, entrypoint: Callable[[], Builder], call: HurricaneCallbackQuery) -> None:
        builder = entrypoint()
        text = builder.text()
        reply_markup = builder.markup()

        await call.edit(text, reply_markup=self.form.create_markup(reply_markup, self.unit_id))
