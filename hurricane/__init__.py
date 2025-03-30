import time

from git import Repo

from hurricane import modloader, types
from hurricane.modloader import Module
from hurricane.fsm import Conversation
from hurricane import utils
from hurricane import inline

__version__ = "0.6.2"
__authors__ = ["sqlmerr"]
__license__ = "GPLv3"

repo = Repo(".")
commit_hex = repo.commit().hexsha
repository_url = "https://github.com/sqlmerr/hurricane"
init_time = time.time()

__all__ = ("modloader", "types", "Module", "Conversation", "utils", "inline")
