import asyncio
import os
import threading
import time

from db import Status, db, initial_status
from scraper import get_site_status
from telegram import Bot
from telegram.request import HTTPXRequest

INTERVAL = int(os.environ.get("INTERVAL", 30))


def pretty_print_statuses(statuses):
    print(
        f"malta: {statuses['malt'][0]}\ncerveza: {statuses['beer'][0]} \n"
        f"cerveza bucanero: {statuses['bucanero_beer'][0]}"
    )


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

        pretty_print_statuses(all_statuses)

        for user in users:
            if not user.status:
                user.status = initial_status
            if current_cerveza_status != user.status["cerveza_last_status"]:
                await self.notify_user(current_cerveza_status, user, "cerveza cristal", beer_site)
                user.status["cerveza_last_status"] = current_cerveza_status

            if current_bucanero_cerveza_status != user.status["cerveza_bucanero_last_status"]:
                await self.notify_user(current_bucanero_cerveza_status, user, "cerveza bucanero", bucanero_beer_site)
                user.status["cerveza_bucanero_last_status"] = current_bucanero_cerveza_status

            if current_malta_status != user.status["malta_last_status"]:
                await self.notify_user(current_malta_status, user, "malta", malta_site)
                user.status["malta_last_status"] = current_malta_status

        db.bulk_update_users(users)
        print(users)

    async def notify_user(self, status, user, item, url):
        print("notifying", user.id, item, status)
        time.sleep(1)
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
    ticker = threading.Event()
    while not ticker.wait(INTERVAL):
        request = HTTPXRequest(connection_pool_size=8, pool_timeout=5.0)
        job = TheArmagedon(Bot(token=token, request=request))
        job.run()
