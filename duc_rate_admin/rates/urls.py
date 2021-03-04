from django.urls import path
from duc_rate_admin.rates.views import RateRequest

urlpatterns = [
    path('', RateRequest.as_view())
]
