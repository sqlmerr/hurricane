import dataclasses
import logging
import inspect

from typing import Callable, Any, Awaitable, TypeVar

log = logging.getLogger(__file__)
V = TypeVar("V")
EventCallback = Callable[[V, dict], Awaitable[Any]] | Callable[[], Awaitable[Any]]


@dataclasses.dataclass(frozen=True)
class EventHandler:
    callback: EventCallback


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def subscribe(self, event: str, func: EventCallback) -> None:
        handlers = self._handlers.get(event, [])
        handler = EventHandler(func)
        handlers.append(handler)
        self._handlers[event] = handlers

    def unsubscribe(self, event: str, func: EventCallback) -> bool:
        if not (handlers := self._handlers.get(event)):
            return False

        for i, h in enumerate(handlers):
            if h.callback == func:
                handlers.pop(i)
                self._handlers[event] = handlers
                return True
        return False

    async def publish(self, event: str, val: V, **kwargs):
        for handler in self._handlers.get(event, []):
            try:
                if len(inspect.getfullargspec(handler.callback).args) < 2:
                    await handler.callback()
                else:
                    await handler.callback(val, kwargs)
            except Exception as e:
                log.exception(e)

    async def publish_first(self, event: str, val: V, **kwargs) -> Any:
        for handler in self._handlers.get(event, []):
            try:
                if len(inspect.getfullargspec(handler.callback).args) == 0:
                    response = await handler.callback()
                else:
                    response = await handler.callback(val, kwargs)
                if not response:
                    continue
                return response
            except Exception as e:
                log.exception(e)
