import os
import sys
import time
import requests
import logging
import traceback
from decimal import Decimal
from currencyapicom import Client as CurrencyClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "duc_rate_admin.settings")
import django

django.setup()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from duc_rate_admin.rates.models import UsdRate

CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")

FSYM = "USD"
TSYMS = [
    "INR", "GBP", "EUR", "CAD", "COP", "NGN",
    "BRL", "ARS", "AUD", "JPY", "NZD"
]

class ApiError(Exception):
    pass


def get_currency_rates(tsym, fsyms):
    currency_client = CurrencyClient(CURRENCY_API_KEY)
    response = currency_client.latest(tsym, fsyms)
    data = response["data"]

    rates = {}
    for rate_name, values in data.items():
        rates[rate_name] = values['value']

    return rates

def get_rates_main():

    rates = get_currency_rates(FSYM, TSYMS)
    for rate_name, rate_value in rates.items():
        usd_rate, _ = UsdRate.objects.get_or_create(currency=rate_name)
        usd_rate.rate = Decimal(rate_value)
        usd_rate.save()

        logging.info(f"Updated rate for {rate_name}: {rate_value} USD")


if __name__ == "__main__":
    if not CURRENCY_API_KEY:
        raise Exception("Currency API key is not provided")
    
    while True:
        try:
            get_rates_main()
        except Exception as e:
            logging.error(e)
        
        time.sleep(int(os.getenv("RATES_CHECKER_TIMEOUT", 60)))
