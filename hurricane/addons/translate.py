from hurricane import Module
from hurricane.addons.base import Addon


Translation = dict[str, str]

class TranslateAddon(Addon):
    def __init__(self, mod: Module, ru: Translation, en: Translation) -> None:
        self.mod = mod
        self.translations = {
            "ru": ru,
            "en": en,
        }


    def __call__(self, key: str) -> str:
        lang = self.mod.db.get("settings", "lang", "en")
        t = self.translations[lang].get(key)
        en = self.translations["en"].get(key)
        if t is None and en is None:
            return "Undefined"
        if t is None and en is not None:
            return en
        return t
