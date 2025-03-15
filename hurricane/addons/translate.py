import hurricane
from hurricane.addons.base import Addon


Translation = dict[str, str]
SUPPORTED_LANGUAGES = ["ru", "en"]


class TranslateAddon(Addon):
    def __init__(self, mod: "hurricane.Module", en: Translation | None = None, ru: Translation | None = None) -> None:
        super().__init__(mod)
        self.translations = {
            "ru": ru if ru else {},
            "en": en if en else {},
        }

    def __call__(self, key: str, *args, **kwargs) -> str:
        lang = self.mod.db.get("settings", "lang", "en")
        t = self.translations[lang].get(key)
        en = self.translations["en"].get(key)
        if t is None and en is None:
            return "Undefined"
        if t is None and en is not None:
            return en
        return t.format(*args, **kwargs) if args or kwargs else t

    def __getattr__(self, item: str):
        def wrapper(*args, **kwargs) -> str:
            return self(item, *args, **kwargs)

        return wrapper
