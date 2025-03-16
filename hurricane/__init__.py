from git import Repo

from hurricane import modloader, types
from hurricane.modloader import Module
from hurricane.fsm import Conversation

__version__ = "0.5.2"
__authors__ = ["sqlmerr"]
__license__ = "MIT"

repo = Repo(".")
commit_hex = repo.commit().hexsha
repository_url = "https://github.com/sqlmerr/hurricane"

__all__ = ("modloader", "types", "Module", "Conversation")
