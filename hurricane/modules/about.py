import hurricane

from hurricane import utils
from hurricane.addons.command import CommandContext, simple_command, CommandAddon
from hurricane.addons.translate import TranslateAddon

from pyrogram.types import Message


class AboutMod(hurricane.Module):
    name = "about"
    version = hurricane.__version__
    developer = "hurricane"
    
    def __init__(self):
        self.t = TranslateAddon(self, en={}, ru={})
        
        self.c = CommandAddon(self)
        # self.c.register(
        #     simple_command("about", )
        # )
        
