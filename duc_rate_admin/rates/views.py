import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from duc_rate_admin.rates.api import get_usd_prices
from duc_rate_admin.rates.models import DucRate


rates_response = openapi.Response(
    description='DUC, DUCX rates',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'DUC': openapi.Schema(type=openapi.TYPE_STRING),
            'DUCX': openapi.Schema(type=openapi.TYPE_STRING)
            },
    )
)


class RateRequest(APIView):
    @swagger_auto_schema(
        operation_description="rate request",
        responses={200: rates_response}
    )
    def get(self, request):
        fsym = request.query_params.get('fsym')
        tsyms = request.query_params.get('tsyms')

        if fsym and tsyms:
            tsyms_list = tsyms.split(',')
            response = {tsym: convert(fsym, tsym) for tsym in tsyms_list}
        else:
            # return just DUC and DUCX to USD rate
            fsyms = ('DUC', 'DUCX')
            tsym = 'USD'

            response = {}
            for fsym in fsyms:
                response[fsym] = {tsym: convert(fsym, tsym)}

        return Response(response, status=status.HTTP_200_OK)


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