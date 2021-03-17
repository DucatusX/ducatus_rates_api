from django.urls import path
from duc_rate_admin.rates.views import RateRequest, RateChangeRequest

urlpatterns = [
    path('', RateRequest.as_view()),
]
