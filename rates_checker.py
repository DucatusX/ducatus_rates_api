import os
import sys
import time
import json
import requests
import logging
import traceback
from decimal import Decimal
import everapi.exceptions
from currencyapicom import Client as CurrencyClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "duc_rate_admin.settings")
import django

django.setup()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

from duc_rate_admin.rates.models import UsdRate, DucRate

CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
COINGECKO_API = os.getenv("COINGECKO_API")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
CURRENCY_API_TIMEOUT = float(os.getenv("CURRENCY_API_TIMEOUT", 10))


FSYM = "USD"
TSYMS = [
    "INR", "GBP", "EUR", "CAD", "COP", "NGN",
    "BRL", "ARS", "AUD", "JPY", "NZD"
]

class ApiError(Exception):
    pass


class TimeoutCurrencyClient(CurrencyClient):
    def _request(self, url, method="GET", params=dict(), data=None, return_type=None):
        url = self.api_base + url

        if self.api_key:
            self.headers["apikey"] = self.api_key

        if method in ["GET", "DELETE"]:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                timeout=CURRENCY_API_TIMEOUT,
            )
        elif method == "POST":
            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=CURRENCY_API_TIMEOUT,
            )
        else:
            raise Exception("Method not supported")

        if response.status_code == 429:
            if "x-ratelimit-remaining-quota-month" in response.headers:
                quota = response.headers["x-ratelimit-remaining-quota-month"]
                if int(quota) <= 0:
                    raise everapi.exceptions.QuotaExceeded()
                raise everapi.exceptions.RateLimitExceeded()
        elif response.status_code == 403:
            raise everapi.exceptions.NotAllowed()
        elif response.status_code == 401:
            raise everapi.exceptions.IncorrectApikey()

        response_obj = json.loads(response.text)

        if "errors" in response_obj:
            raise everapi.exceptions.ApiError(
                "API returned errors:", response_obj["errors"]
            )

        return response_obj


def get_currency_rates(tsym, fsyms):
    currency_client = TimeoutCurrencyClient(CURRENCY_API_KEY)
    try:
        response = currency_client.latest(tsym, fsyms)
    except requests.Timeout:
        logging.error("Currencyapi request timed out after %s seconds", CURRENCY_API_TIMEOUT)
        return {}
    except requests.RequestException as exc:
        logging.error("Currencyapi request failed: %s", exc)
        return {}

    if not isinstance(response, dict):
        logging.error("Unexpected response type from currencyapi: %s", type(response).__name__)
        return {}

    data = response.get("data")
    if not data:
        error = response.get("error")
        if error:
            logging.error("Currencyapi error response: %s", error)
        else:
            logging.error("Currencyapi response has no 'data': %s", response)
        return {}

    rates = {}
    for rate_name, values in data.items():
        rates[rate_name] = values['value']

    return rates


def get_rate_coingecko(coin_id, currencies_id):
    endpoint = COINGECKO_API.format(coin_id, currencies_id)
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": COINGECKO_API_KEY
    }

    response = requests.get(url=endpoint, headers=headers)
    if response.ok:
        rate_value = response.json().get(coin_id, {}).get(currencies_id)
        if rate_value:
            return rate_value

    logging.error(f"Error while trying get {currencies_id} rate for {coin_id} (status code: {response.status_code})")
    return None


def update_bnb_rate():
    bnb_usd_rate = get_rate_coingecko("binancecoin", "usd")
    if bnb_usd_rate:
        bnb_rate, _ = DucRate.objects.get_or_create(currency="BNB")
        bnb_rate.rate = Decimal(bnb_usd_rate)
        bnb_rate.save()

        logging.info(f"Updated rate for BNB: {bnb_usd_rate} USD")

def update_duc_ducx_rates():
    ducx_usd_rate = get_rate_coingecko("ducatus", "usd")
    if ducx_usd_rate:
        ducx_rate_obj, _ = DucRate.objects.get_or_create(currency="DUCX")
        ducx_rate_obj.rate = Decimal(ducx_usd_rate)
        ducx_rate_obj.save()

        logging.info(f"Updated rate for DUCX: {ducx_usd_rate} USD")

def get_rates_main():
    rates = get_currency_rates(FSYM, TSYMS)
    if not rates:
        logging.warning("Skipping USD rates update: no rates returned from currencyapi")
        return

    for rate_name, rate_value in rates.items():
        usd_rate, _ = UsdRate.objects.get_or_create(currency=rate_name)
        usd_rate.rate = Decimal(rate_value)
        usd_rate.save()

        logging.info(f"Updated rate for {rate_name}: {rate_value} USD")


if __name__ == "__main__":
    if not all([CURRENCY_API_KEY, COINGECKO_API, COINGECKO_API_KEY]):
        raise Exception("API keys or API url is not provided")

    BNB_CHECKER_TIMEOUT = int(os.getenv("BNB_CHECKER_TIMEOUT", 60))
    RATES_CHECKER_TIMEOUT = int(os.getenv("RATES_CHECKER_TIMEOUT", 86400))

    DELAY = 1
    start = 0

    while True:
        if not bool(start % RATES_CHECKER_TIMEOUT):
            try:
                get_rates_main()
            except Exception as e:
                logging.error(e)
            try:
                update_duc_ducx_rates()
            except Exception as e:
                logging.error(e)

        if not bool(start % BNB_CHECKER_TIMEOUT):
            try:
                update_bnb_rate()
            except Exception as e:
                logging.error(e)

        time.sleep(DELAY)
        start += DELAY
