import abc
from typing import Callable, Awaitable, Any

from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from hurricane.addons.inline.form import FormAddon
from hurricane.inline.custom import HurricaneCallbackQuery
from hurricane.types import ReplyMarkup


class Component(abc.ABC):
    def __init__(self, *, name: str | None = None):
        self.name = name if name is not None else self.__class__.__name__


class TextComponent(Component):
    def render_text(self) -> str:
        return self._render_text()

    @abc.abstractmethod
    def _render_text(self) -> str:
        raise NotImplementedError


class ButtonComponent(Component):
    def render_button(self) -> dict:
        return self._render_button()

    @abc.abstractmethod
    def _render_button(self) -> dict:
        raise NotImplementedError


class Text(TextComponent):
    def __init__(self, text: str):
        self.text = text
        super().__init__()

    def _render_text(self) -> str:
        return self.text

class ClickableButton(ButtonComponent):
    def __init__(self, text: str, on_click: Any, *args, **kwargs):
        self.text = text
        self.on_click = on_click
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def _render_button(self) -> dict:
        return {"text": self.text, "callback": self.on_click, "args": self.args, "kwargs": self.kwargs}

class UrlButton(ButtonComponent):
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url
        super().__init__()

    def _render_button(self) -> dict:
        return {"text": self.text, "url": self.url}

class RawButton(ButtonComponent):
    def __init__(self, data: dict[str, Any]):
        self.data = data
        super().__init__()

    def _render_button(self) -> dict:
        return self.data

class Builder:
    def __init__(self, components: list[TextComponent | ButtonComponent]) -> None:
        self._components = components

    def _text(self) -> str:
        text = "\n".join([component.render_text() for component in self._components if isinstance(component, TextComponent)])
        for component in self._components:
            print("c: ", component.name)

        return text


    def _markup(self) -> ReplyMarkup:
        buttons = []
        for component in self._components:
            if isinstance(component, ButtonComponent):
                buttons.append(component.render_button())


        return buttons


    async def build(self, message: Message, form: FormAddon):
        text = self._text()
        reply_markup = self._markup()
        print(text, reply_markup, self._components)
        await form.new(message, text, reply_markup)
