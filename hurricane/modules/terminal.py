import os
import asyncio
import hurricane

from hurricane.addons.translate import TranslateAddon
from hurricane.addons.command import CommandAddon, CommandContext, simple_command
from pyrogram.types import Message

async def exec(cmd: str):
    sp = await asyncio.create_subprocess_shell(
        cmd.strip(), 
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=hurricane.utils.get_base_path()
    )
    
    if not (out := await sp.stdout.read(-1)):
        try:
            return (await sp.stderr.read(-1)).decode()
        except UnicodeDecodeError:
            return f'Unicode decode error: {(await sp.stderr.read(-1))}'
    else:
        try:
            return out.decode()
        except UnicodeDecodeError:
            return f'Unicode decode error: {out}'


class TerminalModule(hurricane.Module):
    name = "terminal"
    developer = "sqlmerr"
    version = hurricane.__version__

    def __init__(self):
        self.t = TranslateAddon(self, en={
            "result_txt": (
                "<emoji id=5472111548572900003>⌨️</emoji> <b>Command</b>: <pre language='bash'><code><{cmd}/code></pre>\n"
                "💾 <b>Output:</b> <blockquote>{result}</blockquote>"
            )
        }, ru={
            "result_txt": (
                "<emoji id=5472111548572900003>⌨️</emoji> <b>Команда</b>: <pre language='bash'><code><{cmd}/code></pre>\n"
                "💾 <b>Вывод:</b> <blockquote>{result}</blockquote>"
            )
        })
        self.c = CommandAddon(self)
        self.c.register(simple_command("terminal", self.terminal, is_global=True))

    async def terminal(self, message: Message, context: CommandContext) -> None:
        cmd = context.args
        output = await exec(cmd)
        
        await self.respond(message, self.t.result_txt(cmd=cmd, result=output))
