import contextlib
import io
import html

import meval
from pyrogram.types import Message

import hurricane
from hurricane.addons.command import CommandContext, simple_command
from hurricane.addons.translate import TranslateAddon


class Eval(hurricane.Module):
    developer = "sqlmerr"
    version = hurricane.__version__
    name = "eval"

    def __init__(self) -> None:
        self.t = TranslateAddon(
            self,
            ru={
                "eval_text": (
                    "💻 <b>Код:</b>\n"
                    "<pre><code language='python'>{}</code></pre>\n\n"
                    "✅ <b>Результат:</b>\n"
                    "<pre><code language='python'>{}</code></pre>\n"
                    "💾 <b>Вывод:</b>\n"
                    "<pre><code language='python'>{}</code></pre>"
                ),
                "error": (
                    "💻 <b>Код:</b>\n"
                    "<pre><code language='python'>{}</code></pre>\n\n"
                    "❌ <b>Ошибка:</b>\n"
                    "<pre><code language='python'>{}</code></pre>\n"
                ),
            },
            en={
                "eval_text": (
                    "💻 <b>Code:</b>\n"
                    "<pre><code language='python'>{}</code></pre>\n\n"
                    "✅ <b>Result:</b>\n"
                    "<pre><code language='python'>{}</code></pre>\n"
                    "💾 <b>Print:</b>\n"
                    "<pre><code language='python'>{}</code></pre>"
                ),
                "error": (
                    "💻 <b>Code:</b>\n"
                    "<pre><code language='python'>{}</code></pre>\n\n"
                    "❌ <b>Error:</b>\n"
                    "<pre><code language='python'>{}</code></pre>\n"
                ),
            },
        )
        self.commands.register(
            simple_command("eval", self.eval_cmd, is_global=True, aliases=["e"])
        )

    async def eval_cmd(self, message: Message, context: CommandContext) -> None:
        code = context.args
        reply = message.reply_to_message
        args = {
            "message": message,
            "m": message,
            "reply": reply,
            "r": reply,
            "self": self,
            "client": self.client,
            "c": self.client,
            "db": self.db,
        }

        try:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = str(await meval.meval(code, globals(), **args))

            print_result = stdout.getvalue()
        except Exception as e:
            await message.edit(self.t("error").format(code, e))
            return

        text = self.t("eval_text").format(
            code,
            html.escape(result),
            html.escape(print_result) if print_result else "None",
        )
        await message.edit(text)
