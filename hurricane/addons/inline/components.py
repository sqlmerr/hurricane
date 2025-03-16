import abc
from typing import Any

from aiogram.types import Message

from hurricane.addons.inline.form import FormAddon
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
    def render_button(self) -> list[dict]:
        return self._render_button()

    @abc.abstractmethod
    def _render_button(self) -> list[dict]:
        raise NotImplementedError


class PositionComponent(Component):
    def render(self) -> list[list[dict]]:
        return self._render()

    @abc.abstractmethod
    def _render(self) -> list[list[dict]]:
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

    def _render_button(self) -> list[dict]:
        return [
            {
                "text": self.text,
                "callback": self.on_click,
                "args": self.args,
                "kwargs": self.kwargs,
            }
        ]


class UrlButton(ButtonComponent):
    def __init__(self, text: str, url: str):
        self.text = text
        self.url = url
        super().__init__()

    def _render_button(self) -> list[dict]:
        return [{"text": self.text, "url": self.url}]


class RawButton(ButtonComponent):
    def __init__(self, data: dict[str, Any]):
        self.data = data
        super().__init__()

    def _render_button(self) -> list[dict]:
        return [self.data]


class Group(PositionComponent):
    def __init__(self, *components: ButtonComponent, width: int = 3):
        super().__init__()
        self.components = components
        self.width = width

    def _render(self) -> list[list[dict]]:
        buttons = []
        row = []
        for c in self.components:
            row.extend(c.render_button())

            if len(row) == self.width:
                buttons.append(row)
                row = []
                continue

        if row:
            buttons.append(row)

        return buttons


class Builder:
    def __init__(
        self, *components: TextComponent | ButtonComponent | PositionComponent
    ) -> None:
        self._components = components

    def text(self) -> str:
        text = "\n".join(
            [
                component.render_text()
                for component in self._components
                if isinstance(component, TextComponent)
            ]
        )

        return text

    def markup(self) -> ReplyMarkup:
        buttons = []
        for component in self._components:
            if isinstance(component, ButtonComponent):
                buttons.append(component.render_button())
            elif isinstance(component, PositionComponent):
                buttons.extend(component.render())

        return buttons

    async def build(self, message: Message, form: FormAddon, **kwargs) -> str:
        text = self.text()
        reply_markup = self.markup()
        return await form.new(message, text, reply_markup, **kwargs)
