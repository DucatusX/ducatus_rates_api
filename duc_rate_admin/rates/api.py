from duc_rate_admin.consts import SUPPORTED_CURRENCIES
from duc_rate_admin.rates.models import DucRate

def get_usd_prices():
    usd_prices = {currency: DucRate.objects.get(currency=currency).rate for currency in SUPPORTED_CURRENCIES}
    print('current rates', usd_prices, flush=True)

    return usd_prices