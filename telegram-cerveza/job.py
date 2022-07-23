import asyncio
import time
from threading import Thread

from db import Status, bulk_save_users, get_users
from scraper import get_beer_status, get_malt_status
from telegram.ext import ContextTypes

INTERVAL = 5


class TheArmagedon:
    def __init__(self, bot) -> None:
        self.bot = bot

    def start_the_circus(self):
        Thread(target=self.run).start()

    async def _start_the_circus(self):
        while True:
            users = get_users()
            malt_status = get_malt_status()
            beer_status = get_beer_status()

            for user in users:
                await self.bot.send_message(chat_id=user["id"], text="Hay cacaaaaa, correeeeee!")
                beer_status_last = user["cerveza_last_status"]
                if beer_status != beer_status_last:
                    await self.notify_user(user, "cerveza")
                    user["cerveza_last_status"] = beer_status
                malt_status_last = user["malta_last_status"]
                if malt_status != malt_status_last:
                    await self.notify_user(user, "malta")
                    user["malta_last_status"] = malt_status

            bulk_save_users(users)

            time.sleep(INTERVAL)

    async def notify_user(self, user, item):
        await self.bot.send_message(chat_id=user["id"], text=f"Hay {item}, correeeeee!")

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self._start_the_circus())
        loop.close()
