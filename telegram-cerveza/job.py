import asyncio
import os
import threading
import time

from db import Status, db
from scraper import get_site_status
from telegram import Bot

INTERVAL = int(os.environ.get("INTERVAL", 30))


class TheArmagedon:
    def __init__(self, bot) -> None:
        self.bot = bot

    async def perform_scraping(self):
        users = db.get_users()
        all_statuses = await get_site_status()

        if not all_statuses:
            print("Failed getting status")
            return

        current_malta_status, malta_site = all_statuses["malt"]
        current_cerveza_status, beer_site = all_statuses["beer"]
        current_bucanero_cerveza_status, bucanero_beer_site = all_statuses["bucanero_beer"]

        print(f"getting state {all_statuses=}")

        for user in users:
            if current_cerveza_status != user.cerveza_last_status:
                await self.notify_user(current_cerveza_status, user, "cerveza cristal", beer_site)
                user.cerveza_last_status = current_cerveza_status

            if current_bucanero_cerveza_status != user.cerveza_bucanero_last_status:
                await self.notify_user(current_bucanero_cerveza_status, user, "cerveza bucanero", bucanero_beer_site)
                user.cerveza_bucanero_last_status = current_bucanero_cerveza_status

            if current_malta_status != user.malta_last_status:
                await self.notify_user(current_malta_status, user, "malta", malta_site)
                user.malta_last_status = current_malta_status

        db.bulk_update_users(users)

    async def notify_user(self, status, user, item, url):
        print("notifying", user.id, item, status)
        if status == Status.NOT_FOUND:
            await self.notify_user_ran_out(user, item)
        else:
            await self.notify_user_found(user, item, url)

    async def notify_user_found(self, user, item, url):
        try:
            await self.bot.send_message(chat_id=user.id, text=f"Llego {item} a la bodega, correeeeee! {url}")
        except Exception as e:
            print(e)

    async def notify_user_ran_out(self, user, item):
        try:
            await self.bot.send_message(chat_id=user.id, text=f"Se acabo la {item}!")
        except Exception as e:
            print(e)

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
