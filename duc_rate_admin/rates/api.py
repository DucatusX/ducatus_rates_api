from decimal import Decimal, InvalidOperation
from django.core.exceptions import ObjectDoesNotExist

from duc_rate_admin.consts import SUPPORTED_CURRENCIES
from duc_rate_admin.rates.models import DucRate, UsdRate
from rest_framework.exceptions import APIException



def get_usd_prices():
    usd_prices = {currency: DucRate.objects.get(currency=currency).rate for currency in SUPPORTED_CURRENCIES}
    print('current rates', usd_prices, flush=True)

    return usd_prices



class CurrencyConverter:
    def __init__(self):
        pass

    def convert(self, fsym, tsym):
        amount = 1
        try:
            if fsym == 'USD':
                return self._convert_basic(tsym, amount, UsdRate)
        
            if tsym == 'USD':
                return self._convert_basic(fsym, amount, DucRate)
            
            converted_amount = self._convert_currency(fsym, amount, tsym)
            if converted_amount is not None:
                return converted_amount
        
            converted_amount = self._convert_currency(tsym, amount, fsym, reverse=True)
            if converted_amount is not None:
                return converted_amount
            
            raise APIException(f"Currency conversion error: Unable to convert from '{fsym}' to '{tsym}'.")

        except (ObjectDoesNotExist, InvalidOperation):
            raise APIException(f"Currency conversion error: Invalid conversion operation for currencies '{fsym}' and '{tsym}'.")

    def _convert_currency(self, fsym, amount, tsym, reverse=False):
        try:
            if not reverse:
                rate_to_usd = DucRate.objects.get(currency=fsym).rate
                rate_from_usd = UsdRate.objects.get(currency=tsym).rate
                amount_in_usd = Decimal(amount) * rate_to_usd
                return amount_in_usd * rate_from_usd
            else:
                rate_to_usd = DucRate.objects.get(currency=tsym).rate
                rate_from_usd = UsdRate.objects.get(currency=fsym).rate
                amount_in_usd = Decimal(amount) / rate_to_usd
                return amount_in_usd / rate_from_usd

        except (ObjectDoesNotExist, InvalidOperation):
            return None
        
    def _convert_basic(self, sym, amount , model):
        try:
            rate = model.objects.get(currency=sym).rate
            return Decimal(amount) * rate
        except ObjectDoesNotExist:
            raise ValueError(f"Currency conversion error: The currency '{sym}' is not available.")
