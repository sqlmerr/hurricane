import hurricane

class Addon:
    def __init__(self, mod: "hurricane.Module") -> None:
        self.mod = mod
        self.mod.addons.append(self)
