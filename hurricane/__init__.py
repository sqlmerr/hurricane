from git import Repo

from hurricane import modloader, types
from hurricane.modloader import Module
from hurricane.fsm import Conversation

__version__ = "0.5.0"
__authors__ = ["sqlmerr"]
__license__ = "MIT"

commit_hex = Repo(".").commit().hexsha

__all__ = ("modloader", "types", "Module", "Conversation")
