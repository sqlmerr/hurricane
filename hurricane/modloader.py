import logging
import os
import random
import sys
from importlib.abc import SourceLoader
from importlib.util import spec_from_file_location, module_from_spec
from importlib.machinery import ModuleSpec
from inspect import isclass
from typing import Any, TypeVar, Callable, Awaitable

from pyrogram import Client

from hurricane.addons.base import Addon
from hurricane.database import Database
from hurricane.database.assets import AssetManager
from hurricane.inline.base import InlineManager
from hurricane.types import JSON
from hurricane.utils import create_asset_chat

logger = logging.getLogger(__name__)

DEFAULT_MODS = ("loader", "test", "eval", "settings", "help", "security")

T = TypeVar("T", bound=Addon)


class Module:
    name: str
    developer: str
    version: str | None
    dependencies: list[str] # list of modules

    client: Client
    db: Database
    loader: "ModuleLoader"
    inline: InlineManager
    assets: AssetManager
    addons: list[Addon]

    async def on_load(self):
        pass

    def find_addon(self, addon: type[T]) -> T | None:
        for instance in self.addons:
            if isinstance(instance, addon):
                return instance

    def get(self, key: str, default: JSON = None) -> JSON:
        return self.db.get(self.name, key, default)

    def set(self, key: str, value: JSON) -> None:
        return self.db.set(self.name, key, value)

    def pop(self, key: str) -> None:
        return self.db.pop(self.name, key)

    async def create_asset_chat(
        self,
        title: str,
        desc: str = "",
        supergroup: bool = False,
        invite_bot: bool = False,
        archive: bool = False,
        avatar: str | None = None,
    ):
        return await create_asset_chat(
            self.client,
            self.loader,
            title=title,
            desc=desc,
            supergroup=supergroup,
            invite_bot=invite_bot,
            archive=archive,
            avatar=avatar,
        )


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
    def __init__(self, client: Client, db: Database, inline: InlineManager) -> None:
        self._client = client
        self._db = db
        self.inline = inline
        self.modules: dict[str, Module] = {}
        
        self.__internal_event_handlers: list[dict[str, Callable[[], Awaitable[None]] | str]] = []

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
    ) -> Module | None:
        spec = spec or spec_from_file_location(name, path)
        module = module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)

        for key, value in vars(module).items():
            if isclass(value) and issubclass(value, Module):
                not_installed_deps = []
                for dep in value.dependencies:
                    if dep.lower() not in self.modules.keys():
                        not_installed_deps.append(dep.lower())
                if not_installed_deps:
                    raise ValueError(f"some dependent modules not installed: {not_installed_deps}", not_installed_deps)
                value.name = value.name or name
                value.client = self._client
                value.db = self._db
                value.loader = self
                value.inline = self.inline

                value.addons = []

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
    
    def register_internal_event(self, event: str, func: Callable[[], Awaitable[None]]): 
        self.__internal_event_handlers.append({"event": event, "func": func})
        
    
    async def send_internal_event(self, event: str):
        for h in self.__internal_event_handlers:
            if h.get("event") == event:
                await h.get("func")()
