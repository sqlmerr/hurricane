import asyncio
import json
import logging
import os.path
from csv import excel

from pyrogram.errors import SessionPasswordNeeded, BadRequest
from pyrogram.qrlogin import QRLogin
from datetime import datetime
from getpass import getpass

from pyrogram import Client, enums, raw
from pyrogram.types import User
from qrcode.main import QRCode


def colored_input(prompt: str = "", hide: bool = False) -> str:
    return (input if not hide else getpass)(
        "\x1b[32m{time:%Y-%m-%d %H:%M:%S}\x1b[0m | "
        "\x1b[1m{level: <8}\x1b[0m | "
        "\x1b[0m - \x1b[1m{prompt}\x1b[0m".format(
            time=datetime.now(), level="INPUT", prompt=prompt
        )
    )


YES = ["yes", "y", "д", "да"]
logger = logging.getLogger(__name__)


class Auth:
    def __init__(self) -> None:
        self.client = Client(name="hurricane", parse_mode=enums.ParseMode.HTML)
        self.phone_number = None
        self.password = None

    def _load_credentials(self):
        if not os.path.exists("config.json"):
            data = {}
        else:
            with open("config.json") as f:
                data = json.load(f)
        api_id = data.get("api_id")
        api_hash = data.get("api_hash")

        if not api_id:
            api_id = int(colored_input("Enter api id: "))
            data["api_id"] = api_id
        if not api_hash:
            api_hash = colored_input("Enter api hash: ")
            data["api_hash"] = api_hash
        with open("config.json", mode="w") as f:
            f.write(json.dumps(data))

        self.client.api_id = api_id
        self.client.api_hash = api_hash

    def _use_qr(self) -> bool:
        answer = colored_input("Are we using QR? [Y/n]")
        return answer.lower() in YES

    async def _auth_qr(self) -> User:
        qr_login = QRLogin(self.client)

        while True:
            try:
                logger.info("Scan QR code.")
                signed_in = await qr_login.wait()

                if signed_in:
                    logger.info("Success!")
                    return signed_in
            except asyncio.TimeoutError:
                logger.info("Recreating QR code.")
                await qr_login.recreate()

                qrcode = QRCode(version=1)
                qrcode.add_data(qr_login.url)
                qrcode.print_ascii(invert=True)

            except SessionPasswordNeeded:
                print(f"Password hint: {await self.client.get_password_hint()}")
                return await self.client.check_password(
                    colored_input("Enter 2FA password:", hide=True)
                )

    async def _auth(self) -> User | None:
        logger.info("Authorizing...")

        while True:
            try:
                if not self.phone_number:
                    while True:
                        value = colored_input("Enter phone number:")

                        if value:
                            self.phone_number = value
                            break
                sent_code = await self.client.send_code(self.client.phone_number)
            except Exception as e:
                logger.error(f"Error while authorizing: {e}")
                return
            else:
                break

        sent_code_descriptions = {
            enums.SentCodeType.APP: "Telegram app",
            enums.SentCodeType.SMS: "SMS",
            enums.SentCodeType.CALL: "phone call",
            enums.SentCodeType.FLASH_CALL: "phone flash call",
            enums.SentCodeType.FRAGMENT_SMS: "Fragment SMS",
            enums.SentCodeType.EMAIL_CODE: "email code",
        }

        print(
            f"The confirmation code has been sent via {sent_code_descriptions[sent_code.type]}"
        )

        while True:
            if not self.phone_code:
                self.phone_code = colored_input("Enter confirmation code: ")

            try:
                signed_in = await self.client.sign_in(
                    self.phone_number, sent_code.phone_code_hash, self.phone_code
                )
            except BadRequest as e:
                print(e.MESSAGE)
                self.phone_code = None
            except SessionPasswordNeeded as e:
                print(e.MESSAGE)

                while True:
                    print(
                        "Password hint: {}".format(
                            await self.client.get_password_hint()
                        )
                    )

                    if not self.password:
                        self.password = colored_input(
                            "Enter password (empty to recover): ", hide=True
                        )

                    try:
                        if not self.password:
                            confirm = colored_input("Confirm password recovery (Y/n): ")

                            if confirm in YES:
                                email_pattern = await self.client.send_recovery_code()
                                print(
                                    f"The recovery code has been sent to {email_pattern}"
                                )

                                while True:
                                    recovery_code = colored_input(
                                        "Enter recovery code: "
                                    )

                                    try:
                                        return await self.client.recover_password(
                                            recovery_code
                                        )
                                    except Exception as e:
                                        logger.exception(e)
                                        raise
                            else:
                                self.password = None
                        else:
                            return await self.client.check_password(self.password)
                    except BadRequest as e:
                        print(e.MESSAGE)
                        self.password = None
            else:
                break

    async def authorize(self) -> Client:
        # Client.start()
        self._load_credentials()

        is_authorized = await self.client.connect()
        try:
            if not is_authorized:
                if self._use_qr():
                    await self._auth_qr()
                else:
                    await self.authorize()

            await self.client.invoke(raw.functions.updates.GetState())
        except (Exception, KeyboardInterrupt):
            await self.client.disconnect()
            raise
        else:
            self.client.me = await self.client.get_me()
            await self.client.initialize()

            return self.client
