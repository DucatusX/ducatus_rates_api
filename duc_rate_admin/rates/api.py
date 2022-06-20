from duc_rate_admin.consts import SUPPORTED_CURRENCIES
from duc_rate_admin.rates.models import DucRate


def get_usd_prices():
    usd_prices = {currency: DucRate.objects.get(currency=currency).rate for currency in SUPPORTED_CURRENCIES}
    print('current rates', usd_prices, flush=True)

    return usd_prices


def convert(fsym, tsym):
    coin_list = ('DUC', 'DUCX', 'JAMASY', 'NUYASA', 'SUNOBA', 'DSCMED', 'POG1', 'WDE', 'MDXB', 'G.O.L.D.', 'JWAN', 'TKF', 'AA+')
    rates = {}
    
    for coin in coin_list:
        try:
            rates[coin] = DucRate.objects.get(currency=coin).rate
        except DucRate.DoesNotExist:
            rates[coin] = 1

    if fsym == 'USD' and tsym == 'DUC':
            amount = 1 / rates['DUC']
    elif fsym == 'USD' and tsym == 'DUCX':
            amount = 1 / rates['DUCX']
    elif fsym in str(coin_list) and tsym == 'USD':
         amount = rates[fsym]
    else:
        amount = 1
        
    print(f'amount: {amount}')
    
    return amount