import requests
from bs4 import BeautifulSoup


class Status:
    FOUND = 1
    NOT_FOUND = 2


SITE = "https://micerveza.com/sucursal/hol"

BEER_SITE = SITE + "/cerveza-cristal-24-latas-de-33-cl-alc-5-4-vol.html"
MALT_SITE = SITE + "/caja-malta.html"


def get_status(response):
    soup = BeautifulSoup(response.text, "lxml")
    for item in soup.find_all("div", class_="product-info-stock-sku"):
        if "unavailable" not in item.div["class"]:
            return Status.FOUND
    return Status.NOT_FOUND


def get_beer_status():
    return get_status(requests.get(BEER_SITE))


def get_malt_status():
    return get_status(requests.get(MALT_SITE))
