import logging
import os
import random
import sys
from importlib.abc import SourceLoader
from importlib.util import spec_from_file_location, module_from_spec
from importlib.machinery import ModuleSpec
from inspect import isclass
from typing import Any

from pyrogram import Client

from hurricane.addons.base import Addon
from hurricane.addons.command import CommandAddon
from hurricane.database import Database
from hurricane.types import JSON

logger = logging.getLogger(__name__)

DEFAULT_MODS = ["loader", "test", "eval", "settings", "help"]


class Module:
    name: str
    developer: str
    version: str | None

    commands: CommandAddon
    client: Client
    db: Database
    loader: "ModuleLoader"
    addons: list[Addon]

    async def on_load(self):
        pass

    def get(self, key: str, default: JSON = None) -> JSON:
        return self.db.get(self.name, key, default)

    def set(self, key: str, value: JSON) -> None:
        return self.db.set(self.name, key, value)

    def pop(self, key: str) -> None:
        return self.db.pop(self.name, key)


class StringLoader(SourceLoader):
    def __init__(self, data: str, origin: str) -> None:
        self.data = data.encode("utf-8")
        self.origin = origin

    def get_code(self, full_name: str) -> Any | None:
        source = self.get_source(full_name)
        if not source:
            return None

        return compile(source, self.origin, "exec", dont_inherit=True)

    def get_filename(self, _: str) -> str:
        return self.origin

    def get_data(self, _: str) -> bytes:
        return self.data


class ModuleLoader:
    def __init__(self, client: Client, db: Database) -> None:
        self._client = client
        self._db = db
        self.modules: dict[str, Module] = {}

    async def load(self) -> None:
        module_dir = "hurricane/modules"
        external_module_dir = "hurricane/loaded_modules"
        modules = os.listdir(os.path.join(".", module_dir))

        if not os.path.exists(os.path.join(".", external_module_dir)):
            os.makedirs(os.path.join(".", external_module_dir))
        external_modules = os.listdir(os.path.join(".", external_module_dir))
        for module in filter(
            lambda p: p.endswith(".py") and p != "__init__.py", modules
        ):
            module_path = os.path.join(os.path.abspath("."), module_dir, module)
            module_name = module[:-3]

            mod = await self.load_module(module_name, module_path)

        for external_mod in filter(
            lambda p: p.endswith(".py") and p != "__init__.py", external_modules
        ):
            module_path = os.path.join(
                os.path.abspath("."), external_module_dir, external_mod
            )
            module_name = external_mod[:-3]

            mod = await self.load_module(module_name, module_path)

    def load_instance(
        self, name: str, path: str = "", spec: ModuleSpec | None = None
    ) -> Module:
        spec = spec or spec_from_file_location(name, path)
        module = module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)

        instance = None

        for key, value in vars(module).items():
            if isclass(value) and issubclass(value, Module):
                value.name = value.name or name
                value.client = self._client
                value.db = self._db
                value.loader = self

                command_addon = CommandAddon(self._client, name)
                value.addons = [command_addon]
                value.commands = command_addon

                instance = value()

                return instance

    async def load_module(
        self, name: str, path: str = "", spec: ModuleSpec | None = None
    ) -> Module | None:
        instance = self.load_instance(name, path, spec)
        if not instance:
            logger.warning("No module found at %s", path)
            return None
        self.modules[instance.name.lower()] = instance

        await instance.on_load()

        return instance

    async def load_third_party_module(
        self, source: str, origin: str = "<string>"
    ) -> str | None:
        name = f"hurricane.modules.{random.randint(1, 99999)}"
        try:
            spec = ModuleSpec(name, origin=origin, loader=StringLoader(source, origin))

            instance = self.load_instance(name, source, spec)
            if instance.name.lower().strip() in DEFAULT_MODS:
                return None
            self.modules[instance.name.lower()] = instance
            await instance.on_load()
            return instance.name.lower()

        except Exception as e:
            logger.exception(e)
            return None

    def unload_module(self, module_name: str) -> None:
        if module_name.lower().strip() in DEFAULT_MODS:
            return

        mod = self.modules.get(module_name, None)
        if not mod:
            raise ValueError(f"No module found at {module_name}")

        self.modules.pop(module_name, None)
        os.remove(os.path.join(".", "hurricane/loaded_modules", f"{module_name}.py"))

    def find_module(self, query: str) -> Module | None:
        fltr = list(
            filter(
                lambda p: p.name.lower().strip() == query.lower().strip(),
                self.modules.values(),
            )
        )
        return fltr[0] if len(fltr) > 0 else None
