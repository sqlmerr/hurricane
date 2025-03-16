from typing import Any

from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from pydantic import ConfigDict

from hurricane.types import ReplyMarkup


class HurricaneCallbackQuery(CallbackQuery):
    model_config = ConfigDict(
        use_enum_values=True,
        extra="ignore",
        frozen=False,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        defer_build=True,
    )

    def __init__(
        self,
        call: CallbackQuery,
        manager: Any,
    ) -> None:
        attrs = {
            "id",
            "from_user",
            "chat_instance",
            "message",
            "inline_message_id",
            "chat_instance",
            "data",
            "game_short_name",
        }

        CallbackQuery.__init__(self, **({attr: getattr(call, attr) for attr in attrs}))

        for attr in attrs:
            setattr(self, attr, getattr(call, attr))

        self.as_(manager.bot)

    async def edit(self, text: str, reply_markup: InlineKeyboardMarkup, **kwargs):
        if "inline_message_id" in kwargs:
            kwargs.pop("inline_message_id")

        if not self.inline_message_id:
            await self.message.edit_text(text, reply_markup=reply_markup, **kwargs)
        else:
            await self.bot.edit_message_text(
                inline_message_id=self.inline_message_id,
                text=text,
                reply_markup=reply_markup,
                **kwargs,
            )
