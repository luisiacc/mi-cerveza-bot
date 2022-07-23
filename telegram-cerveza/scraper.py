class Status:
    FOUND = 1
    NOT_FOUND = 2


SITE = "https://micerveza.com/sucursal/hol"

BEER_SITE = SITE + "/cerveza.html"
MALT_SITE = SITE + "/malta.html"


def get_beer_status():
    return 2


def get_malt_status():
    return 2
