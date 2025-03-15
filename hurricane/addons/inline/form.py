from typing import Any

from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery, CopyTextButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pyrogram import Client
from pyrogram.types import Message

import hurricane
from hurricane import utils
from hurricane.addons.base import Addon
from hurricane.inline.custom import HurricaneCallbackQuery
from hurricane.inline.units import Unit
from hurricane.types import ReplyMarkup


class FormAddon(Addon):
    def __init__(self, mod: "hurricane.Module") -> None:
        super().__init__(mod)
        self._forms: dict[str, dict[str, Any]] = {}
        self._callback_map: dict[str, dict[str, Any]] = {}

    async def _inline_handler(self, query: InlineQuery, uid: str):
        form = self._forms.get(uid)
        if not form:
            return

        await query.answer(
            [
                InlineQueryResultArticle(
                    id=uid,
                    title="exec",
                    input_message_content=InputTextMessageContent(
                        message_text=form["text"],
                    ),
                    reply_markup=self.create_markup(form["reply_markup"], uid),
                )
            ]
        )

    async def _callback_handler(self, call: CallbackQuery, uid: str):
        callback = self._callback_map.get(uid)
        if not callback:
            return

        handler = callback["handler"]
        args = callback.get("args", ())
        kwargs = callback.get("kwargs", {})

        query = HurricaneCallbackQuery(call, self.mod.inline)
        await handler(query, *args, **kwargs)

    def __create_button(self, button: dict, unit_id: str) -> InlineKeyboardButton | None:
        text = button["text"]
        if "data" in button:
            return InlineKeyboardButton(text=text, callback_data=button["data"])

        elif "url" in button:
            return InlineKeyboardButton(text=text, url=button["url"])

        elif "callback" in button:
            uid = utils.random_identifier(16)
            self._callback_map[uid] = {
                "handler": button["callback"],
                **(
                    {"args": button["args"]}
                    if button.get("args", None) is not None
                    else {}
                ),
                **(
                    {"kwargs": button["kwargs"]}
                    if button.get("kwargs", None) is not None
                    else {}
                ),
            }
            return InlineKeyboardButton(text=text, callback_data=f"{unit_id}:form:{uid}")
        elif "copy_text" in button:
            return InlineKeyboardButton(text=text, copy_text=CopyTextButton(text=button["copy_text"]))
        elif "action" in button:
            action = button["action"]
            if action == "close":
                return InlineKeyboardButton(text=text, callback_data="close")

    def create_markup(self, markup: ReplyMarkup, unit_id: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        if isinstance(markup, list):
            for r in markup:
                if isinstance(r, list):
                    buttons = []
                    for b in r:
                        if not isinstance(b, dict):
                            raise ValueError("button must be a dict")
                        button = self.__create_button(b, unit_id)
                        if button:
                            buttons.append(button)
                    builder.row(*buttons)
                elif isinstance(r, dict):
                    button = self.__create_button(r, unit_id)
                    if button:
                        builder.add(button)
        elif isinstance(markup, dict):
            button = self.__create_button(markup, unit_id)
            if button:
                builder.add(button)

        else:
            raise ValueError("invalid markup")

        return builder.as_markup()

    async def new(self, message: Message, text: str, reply_markup: ReplyMarkup):
        uid = utils.random_identifier(16)
        self.mod.inline.add_unit(
            Unit(
                "form",
                uid,
                handler=self._inline_handler,
                callback_handler=self._callback_handler,
            )
        )
        self._forms[uid] = {
            "text": text,
            "reply_markup": reply_markup,
            "message": message,
        }

        await message.edit("💥")
        results = await self.mod.client.get_inline_bot_results(
            self.mod.inline.bot_id, f"form:{uid}"
        )
        await self.mod.client.send_inline_bot_result(
            message.chat.id, results.query_id, results.results[0].id
        )

        await message.delete()
