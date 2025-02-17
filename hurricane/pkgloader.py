import logging
import os
import sys
from importlib.util import spec_from_file_location, module_from_spec
from importlib.machinery import ModuleSpec
from inspect import isclass

from pyrogram import Client

from hurricane.addons.base import Addon
from hurricane.addons.command import CommandAddon
from hurricane.database import Database
from hurricane.types import JSON

logger = logging.getLogger(__name__)


class Package:
    name: str
    developer: str
    version: str | None

    commands: CommandAddon
    client: Client
    db: Database
    addons: list[Addon]

    async def on_load(self):
        logger.info(f"Package loaded: {self.developer} {self.version}")

    def get(self, key: str, default: JSON = None) -> JSON:
        return self.db.get(self.name, key, default)

    def set(self, key: str, value: JSON) -> None:
        return self.db.set(self.name, key, value)

    def pop(self, key: str) -> None:
        return self.db.pop(self.name, key)


class PackageLoader:
    def __init__(self, client: Client, db: Database) -> None:
        self._client = client
        self._db = db
        self.packages: dict[str, Package] = {}

    async def load(self, package_dir: os.PathLike = "hurricane/packages") -> None:
        packages = os.listdir(package_dir)
        for package in filter(
            lambda p: p.endswith(".py") and p != "__init__.py", packages
        ):
            package_path = os.path.join(os.path.abspath("."), package_dir, package)
            package_name = package[:-3]

            pkg = self.load_package(package_path, package_name)
            if pkg:
                await pkg.on_load()

    def load_package(
        self, path: str, name: str, spec: ModuleSpec | None = None
    ) -> Package:
        spec = spec or spec_from_file_location(name, path)
        module = module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)

        instance = None

        for key, value in vars(module).items():
            if isclass(value) and issubclass(value, Package):
                value.name = value.name or name
                value.client = self._client
                value.db = self._db

                command_addon = CommandAddon(self._client, name)
                value.addons = [command_addon]
                value.commands = command_addon

                instance = value()

                self.packages[name] = instance

        if not instance:
            logger.warning("No package found at %s", path)

        return instance
