from django.contrib import admin

from duc_rate_admin.rates.models import DucRate


class DucRateAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)

admin.site.register(DucRate, DucRateAdmin)