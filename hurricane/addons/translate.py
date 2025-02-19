from hurricane import Module
from hurricane.addons.base import Addon


Translation = dict[str, str]
SUPPORTED_LANGUAGES = ["ru", "en"]


class TranslateAddon(Addon):
    def __init__(self, mod: Module, en: Translation, ru: Translation) -> None:
        self.mod = mod
        self.translations = {
            "ru": ru,
            "en": en,
        }

    def __call__(self, key: str, *args, **kwargs) -> str:
        lang = self.mod.db.get("settings", "lang", "en")
        t = self.translations[lang].get(key)
        en = self.translations["en"].get(key)
        if t is None and en is None:
            return "Undefined"
        if t is None and en is not None:
            return en
        return t.format(*args, **kwargs)

    def __getattr__(self, item: str):
        def wrapper(*args, **kwargs) -> str:
            return self(item, *args, **kwargs)

        return wrapper
