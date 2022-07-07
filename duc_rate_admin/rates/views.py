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
from duc_rate_admin.consts import SUPPORTED_CURRENCIES
from duc_rate_admin.settings import AUTH_API_KEY


properties = {}
for cur in SUPPORTED_CURRENCIES:
    properties[cur] = openapi.Schema(type=openapi.TYPE_STRING)

rates_response = openapi.Response(
    description=f'Display currency rates. '
                f'Supported currencies: {", ".join(SUPPORTED_CURRENCIES)}',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=properties
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
            fsyms = SUPPORTED_CURRENCIES
            tsym = 'USD'
    
            response = {}
            for fsym in fsyms:
                response[fsym] = {tsym: convert(fsym, tsym)}
        
        return Response(response, status=status.HTTP_200_OK)
