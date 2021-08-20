import os
import sys
import time
import requests
import traceback
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "duc_rate_admin.settings")
import django

django.setup()

from duc_rate_admin.rates.models import DucRate


API_URL = "https://api.coingecko.com/api/v3/coins/{coin_code}"


QUERY_TSYM = "wrapped-ducatusx"
QUERY_FSYM = "usd"


def get_rate(tsym):
    res = requests.get(API_URL.format(coin_code=tsym))
    if res.status_code != 200:
        raise Exception("cannot get exchange rate for {}".format(QUERY_FSYM))
    response = res.json()
    return response["market_data"]["current_price"][QUERY_FSYM]


if __name__ == "__main__":
    while True:
        rate = get_rate(QUERY_TSYM)
        duc_rate, _ = DucRate.objects.get_or_create(currency="DUCX")
        duc_rate.rate = Decimal(rate)
        duc_rate.save()
        time.sleep(int(os.getenv("RATES_CHECKER_TIMEOUT", 60)))
