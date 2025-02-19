from git import Repo

from hurricane import modloader, types
from hurricane.modloader import Module

__version__ = "0.3.0"
__authors__ = ["sqlmerr"]
__license__ = "MIT"

commit_hex = Repo(".").commit().hexsha

__all__ = (
    "modloader",
    "types",
    "Module",
)
