import asyncio
import os
import threading
import time

from db import Status, db
from scraper import get_beer_status, get_malt_status
from telegram import Bot

INTERVAL = int(os.environ.get("INTERVAL", 30))


class TheArmagedon:
    def __init__(self, bot) -> None:
        self.bot = bot

    async def perform_scraping(self):
        users = db.get_users()
        current_malta_status = get_malt_status()
        current_cerveza_status = get_beer_status()
        print(f"getting state {current_malta_status=} {current_cerveza_status=}")

        for user in users:
            last_cerveza_status = user.cerveza_last_status
            if current_cerveza_status != last_cerveza_status:
                await self.notify_user(current_cerveza_status, user, "cerveza")
                user.cerveza_last_status = current_cerveza_status
            last_malta_status = user.malta_last_status
            if current_malta_status != last_malta_status:
                await self.notify_user(current_malta_status, user, "malta")
                user.malta_last_status = current_malta_status

        db.bulk_update_users(users)

    async def notify_user(self, status, user, item):
        if status == Status.NOT_FOUND:
            await self.notify_user_ran_out(user, item)
        else:
            await self.notify_user_found(user, item)

    async def notify_user_found(self, user, item):
        await self.bot.send_message(chat_id=user.id, text=f"Llego {item} a la bodega, correeeeee!")

    async def notify_user_ran_out(self, user, item):
        await self.bot.send_message(chat_id=user.id, text=f"Se acabo la {item}!")

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.perform_scraping())
        loop.close()


if __name__ == "__main__":
    token = os.environ.get("TOKEN", "")
    job = TheArmagedon(Bot(token=token))
    ticker = threading.Event()
    while not ticker.wait(INTERVAL):
        job.run()
