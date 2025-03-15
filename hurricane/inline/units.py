from dataclasses import dataclass
from typing import Callable, Awaitable

from aiogram.types import InlineQuery, CallbackQuery


@dataclass(frozen=True)
class Unit:
    name: str
    uid: str
    handler: Callable[[InlineQuery, str], Awaitable[None]]
    callback_handler: Callable[[CallbackQuery, str], Awaitable[None]]


class UnitManager:
    def __init__(self):
        self._units = []

    def add_unit(self, unit: Unit):
        self._units.append(unit)

    def find_unit(self, uid: str) -> Unit | None:
        for unit in self._units:
            if unit.uid == uid:
                return unit

    @property
    def units(self) -> list[Unit]:
        return self._units
