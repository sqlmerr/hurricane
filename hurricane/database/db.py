import json
from pathlib import Path

from hurricane.types import JSON


class Database:
    def __init__(self, filepath: str | Path) -> None:
        self.location = Path(filepath)
        self.data = self.load()

    def load(self) -> dict[str, JSON]:
        if not self.location.exists():
            return {}

        with self.location.open(mode="r", encoding="utf-8") as file:
            return json.load(file)

    def save(self) -> None:
        with self.location.open("w", encoding="utf-8") as file:
            file.write(json.dumps(self.data, indent=4))

    def set(self, path: str, key: str, value: JSON) -> None:
        self.data.setdefault(path, {})[key] = value
        return self.save()

    def get(self, path: str, key: str, default: JSON = None) -> JSON:
        try:
            return self.data[path][key]
        except KeyError:
            self.set(path, key, default)
            return default

    def pop(self, path: str, key: str) -> None:
        owner = self.data.get(path, {})
        if not isinstance(owner, dict):
            return
        del self.data[path][key]
