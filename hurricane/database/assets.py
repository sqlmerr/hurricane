from pyrogram import Client
from pyrogram.types import Chat, Message

import hurricane.modloader
from hurricane import utils


class AssetManager:
    def __init__(self, loader: "hurricane.modloader.ModuleLoader", client: Client):
        self._loader = loader
        self._client = client
        self._chat: Chat | None = None

    async def load(self):
        self._chat = await utils.create_asset_chat(self._client, self._loader, "hurricane-assets", "Your personal assets will be stored here!", archive=True)

        for mod in self._loader.modules.values():
            mod.assets = self

    async def get(self, m_id: int) -> Message | None:
        msg = await self._client.get_messages(self._chat.id, m_id)
        if not msg:
            return None

        return msg

    async def store(self, message: Message) -> int:
        return (await message.copy(chat_id=self._chat.id)).id