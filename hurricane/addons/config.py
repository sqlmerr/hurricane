import hurricane
import dataclasses

from typing import Type, TypeVar, Callable

from .base import Addon
from hurricane.types import JSON

T = TypeVar("T", bound=JSON)


@dataclasses.dataclass(frozen=True)
class ConfigOption:
    name: str
    type_: Type[T]
    doc: str | Callable[[], str]
    default: T = None


class ConfigAddon(Addon):
    def __init__(self, mod: "hurricane.Module", *options: ConfigOption):
        super().__init__(mod)
        self.options = options
        self._values = self._load()

    def _load(self) -> dict[str, T]:
        values = {}
        options_in_db: dict[str, T] = self.mod.get("_config_", {})
        for option in self.options:
            if option.name not in options_in_db.keys():
                options_in_db[option.name] = option.default
            values[option.name] = options_in_db[option.name]

        self.mod.set("_config_", options_in_db)
        return values

    def __getitem__(self, key: str) -> T:
        return self._values[key]

    def __setitem__(self, key: str, value: T) -> bool:
        val = self[key]
        for option in self.options:
            if option.name != key:
                continue
            if not isinstance(value, option.type_):
                return False
            values = self.mod.get("_config_")
            values[key] = value
            self._values[key] = value
            self.mod.set("_config_", values)
            return True
        return False
