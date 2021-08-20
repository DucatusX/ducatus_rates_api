from django.contrib import admin
from django.urls import path
from django.urls import include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import status
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="duc_rates",
        default_version='v1',
        description="API for duc_rates",
        contact=openapi.Contact(email="ephdtrg@mintyclouds.in"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/rates/', include('duc_rate_admin.rates.urls')),
]

