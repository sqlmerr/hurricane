import logging
from abc import ABC, abstractmethod

from pyrogram import Client
from pyrogram.types import User

from hurricane.database import Database

log = logging.getLogger(__name__)


class BaseRule(ABC):
    @abstractmethod
    def check(self, user: User, client: Client, database: Database) -> bool:
        raise NotImplementedError


class OnlyMe(BaseRule):
    def check(self, user: User, client: Client, database: Database) -> bool:
        return user.id == client.me.id


class In(BaseRule):
    def __init__(self, *user_ids: int) -> None:
        self.user_ids = user_ids

    def check(self, user: User, client: Client, database: Database) -> bool:
        return user.id in self.user_ids


class Owner(BaseRule):
    def check(self, user: User, client: Client, database: Database) -> bool:
        owners = database.get("core.security", "owners", [client.me.id])
        return user.id in owners
