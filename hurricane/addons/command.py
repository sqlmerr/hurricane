from typing import Callable, Awaitable

from pyrogram import Client
from pyrogram.types import Message

from hurricane.addons.base import Addon


def simple_command(command: str, func: "CommandFunc", *, is_global: bool = False):
    return Command(command, is_global=is_global, func=func)


class CommandContext:
    def __init__(self, command: "Command", args: str) -> None:
        self._command = command
        self._args = args

    @property
    def command(self) -> "Command":
        return self._command

    @property
    def args(self) -> str:
        return self._args


CommandFunc = Callable[[Message, CommandContext], Awaitable[None]]


class Command:
    def __init__(self, cmd: str, is_global: bool, func: CommandFunc) -> None:
        self.cmd = cmd
        self.func = func

    async def __call__(self, message: Message, context: CommandContext) -> None:
        await self.func(message, context)


class CommandAddon(Addon):
    def __init__(self, client: Client, package_name: str):
        self.client = client
        self.package_name = package_name
        self._global_commands = {}
        self._commands = {}

    @property
    def global_commands(self) -> dict[str, Command]:
        return self._global_commands

    @property
    def commands(self) -> dict[str, Command]:
        return self._commands

    def _find_command(self, cmd: str, is_global: bool) -> Command | None:
        if is_global:
            for k, v in self._global_commands.items():
                if k == cmd:
                    return v
        else:
            for k, v in self._commands.items():
                if k == cmd:
                    return v

    def register(self, *cmds: Command) -> None:
        for cmd in cmds:
            self._commands[cmd.cmd] = cmd

    async def handle_command(self, command: str, message: Message) -> bool:
        full_cmd = command.split(" ", 1)
        command = full_cmd[0]
        args = full_cmd[1] if len(full_cmd) == 2 else ""
        splitted_cmd = command.split(".", 1)
        is_global = False
        if len(splitted_cmd) == 2:
            is_global = True
            if splitted_cmd[0] != self.package_name:
                return False

        cmd = self._find_command(command, is_global)
        if not cmd:
            return False
        context = CommandContext(command=cmd, args=args)
        await cmd(message, context)

        return True
