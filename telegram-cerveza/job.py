import asyncio
import time
from threading import Thread

from db import Status, db
from scraper import get_beer_status, get_malt_status

INTERVAL = 5


class TheArmagedon:
    def __init__(self, bot) -> None:
        self.bot = bot

    def start_the_circus(self):
        Thread(target=self.run).start()

    async def _start_the_circus(self):
        while True:
            users = db.get_users()
            malt_status = get_malt_status()
            beer_status = get_beer_status()

            for user in users:
                beer_status_last = user.cerveza_last_status
                if beer_status != beer_status_last:
                    await self.notify_user(beer_status, user, "cerveza")
                    user.cerveza_last_status = beer_status
                malt_status_last = user.malta_last_status
                if malt_status != malt_status_last:
                    await self.notify_user(malt_status, user, "malta")
                    user.malta_last_status = malt_status

            db.bulk_update_users(users)

            time.sleep(INTERVAL)

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

        loop.run_until_complete(self._start_the_circus())
        loop.close()
