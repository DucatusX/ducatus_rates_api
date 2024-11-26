from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from duc_rate_admin.rates.api import get_usd_prices, CurrencyConverter
from duc_rate_admin.rates.models import DucRate, UsdRate


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
        manual_parameters=[
            openapi.Parameter(
                "fsym",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Symbol to convert from"
            ),
            openapi.Parameter(
                "tsyms",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Symbol(s) to convert to"
            )
        ],  
        responses={200: rates_response}
    )
    def get(self, request):
        fsym = request.query_params.get('fsym')
        tsyms = request.query_params.get('tsyms')

        converter = CurrencyConverter()

        if fsym and tsyms:
            tsyms_list = tsyms.split(',')
            self.validate_tsyms(tsyms_list)

            response = {tsym: converter.convert(fsym, tsym) for tsym in tsyms_list}
        else:
            fsyms = DucRate.objects.values_list("currency", flat=True)
            tsyms_list = UsdRate.objects.values_list("currency", flat=True)
            response = {}
            for fsym in fsyms:
                response[fsym] = {tsym: converter.convert(fsym, tsym) for tsym in tsyms_list}

        return Response(response, status=status.HTTP_200_OK)
    
    def validate_tsyms(self, tsyms):
        available_tsyms = UsdRate.get_available_tsyms() + ['USD']
        for tsym in tsyms:
            if tsym not in available_tsyms:
                raise ValidationError(f"Tsym is not supported: {tsym}")
