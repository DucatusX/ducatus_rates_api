from duc_rate_admin.consts import SUPPORTED_CURRENCIES
from duc_rate_admin.rates.models import DucRate


def get_usd_prices():
    usd_prices = {currency: DucRate.objects.get(currency=currency).rate for currency in SUPPORTED_CURRENCIES}
    print('current rates', usd_prices, flush=True)

    return usd_prices


def convert(fsym, tsym):
    duc_usd_price = DucRate.objects.get(currency='DUC').rate
    ducx_usd_price = DucRate.objects.get(currency='DUCX').rate

    if fsym == 'USD' and tsym == 'DUC':
            amount = 1 / duc_usd_price
    elif fsym == 'USD' and tsym == 'DUCX':
            amount = 1 / ducx_usd_price
    elif fsym == 'DUC' and tsym == 'USD':
            amount = duc_usd_price
    elif fsym == 'DUCX' and tsym == 'USD':
            amount = ducx_usd_price
    else:
        amount = 1
    print(f'amount: {amount}')
    return amount