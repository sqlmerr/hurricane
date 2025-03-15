from abc import ABC, abstractmethod

from pyrogram import Client
from pyrogram.types import User


class BaseRule(ABC):
    @abstractmethod
    def check(self, user: User, client: Client) -> bool:
        raise NotImplementedError


class Me(BaseRule):
    def check(self, user: User, client: Client) -> bool:
        return user.id == client.me.id

class In(BaseRule):
    def __init__(self, *user_ids: int) -> None:
        self.user_ids = user_ids

    def check(self, user: User, client: Client) -> bool:
        return user.id in self.user_ids
