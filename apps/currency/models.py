# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.conf import settings
from django.db import models

from solo.models import SingletonModel


class EUR(SingletonModel):
    rate = models.DecimalField('Курс евро', max_digits=4, decimal_places=2, default=Decimal('71.18'))
    update_dt = models.DateTimeField('Дата последнего обновления', editable=False, auto_now=True)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True, editable=False)

    class Meta:
        verbose_name = 'EUR'

    def __unicode__(self):
        return 'Курс евро'

    @classmethod
    def get_rate(cls):
        obj = cls.get_solo()
        return obj.rate


class USD(SingletonModel):
    rate = models.DecimalField('Курс доллара', max_digits=4, decimal_places=2, default=Decimal('61.98'))
    update_dt = models.DateTimeField('Дата последнего обновления', editable=False, auto_now=True)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True, editable=False)

    class Meta:
        verbose_name = 'USD'

    def __unicode__(self):
        return 'Курс доллара'

    @classmethod
    def get_rate(cls):
        obj = cls.get_solo()
        return obj.rate
