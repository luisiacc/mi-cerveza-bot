import asyncio

import aiohttp
from bs4 import BeautifulSoup


class Status:
    FOUND = 1
    NOT_FOUND = 2


SITE = "https://micerveza.com/sucursal/hol"

BEER_SITE = SITE + "/cerveza-cristal-24-latas-de-33-cl-alc-5-4-vol.html"
BUCANERO_BEER_SITE = SITE + "/cerveza-bucanero-24-latas-de-355ml-alc-5-4-vol.html"
MALT_SITE = SITE + "/caja-malta.html"


async def get(session, url):
    async with session.get(url) as response:
        return await response.text()


def get_status(text):
    soup = BeautifulSoup(text, "lxml")
    for item in soup.find_all("div", class_="product-info-stock-sku"):
        if "unavailable" not in item.div["class"]:
            return Status.FOUND
    return Status.NOT_FOUND


async def get_beer_status(session):
    return get_status(await get(session, BEER_SITE))


async def get_bucanero_beer_status(session):
    return get_status(await get(session, BUCANERO_BEER_SITE))


async def get_malt_status(session):
    return get_status(await get(session, MALT_SITE))


async def get_site_status():
    responses = []
    tasks = []
    async with aiohttp.ClientSession() as session:
        tasks.append(asyncio.ensure_future(get_beer_status(session)))
        tasks.append(asyncio.ensure_future(get_bucanero_beer_status(session)))
        tasks.append(asyncio.ensure_future(get_malt_status(session)))
        responses = await asyncio.gather(*tasks)

    beer_status, bucanero_beer_status, malt_status = responses
    return {
        "beer": (beer_status, BEER_SITE),
        "bucanero_beer": (bucanero_beer_status, BUCANERO_BEER_SITE),
        "malt": (malt_status, MALT_SITE),
    }
