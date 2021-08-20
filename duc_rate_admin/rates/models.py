from django.db import models
from django.db.models.signals import post_save

from duc_rate_admin.consts import MAX_AMOUNT_LEN
from duc_rate_admin.consts import CHANGE_RATE


class DucRate(models.Model):
    currency = models.CharField(max_length=20, unique=True)
    rate = models.DecimalField(max_digits=MAX_AMOUNT_LEN, decimal_places=8, default=0.06)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.currency


def change_related(sender, instance, created, **kwargs):
    '''
    get_or_create is for creating first models after deploy
    '''
    if instance.currency == 'DUCX':
        duc, _ = DucRate.objects.get_or_create(currency='DUC')
        duc.rate = instance.rate / CHANGE_RATE
        duc.save()


post_save.connect(change_related, sender=DucRate)
