import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from duc_rate_admin.rates.api import get_usd_prices, convert
from duc_rate_admin.rates.models import DucRate
from duc_rate_admin.settings import AUTH_API_KEY


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


class RateChangeRequest(APIView):

    def post(self, request):
        data = request.data

        api_key = data.get('api-key')

        if not api_key:
            raise PermissionDenied
        else:
            if api_key != AUTH_API_KEY:
                raise PermissionDenied

        duc_price = data.get('DUC')
        ducx_price = data.get('DUCX')
        duc_price_obj = DucRate.objects.get(currency='DUC')
        ducx_price_obj = DucRate.objects.get(currency='DUCX')
        print(duc_price)
        print(ducx_price)

        if duc_price:
            duc_price_obj.rate = float(duc_price)
            print(duc_price_obj.rate)
            duc_price_obj.save()

        if ducx_price:
            ducx_price_obj.rate = float(ducx_price)
            print(ducx_price_obj.rate)
            ducx_price_obj.save()

        return Response({'DUC': duc_price_obj.rate, 'DUCX': ducx_price_obj.rate}, status=status.HTTP_200_OK)