# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CallbackOrder(models.Model):
    datetime = models.DateTimeField('Дата и время', auto_now_add=True)
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Профиль', blank=True, null=True)

    name = models.CharField(_('Имя'), max_length=255)
    phone = models.CharField(_('Телефон'), max_length=30)

    class Meta:
        ordering = ['-datetime', ]
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы обратного звонка'

    def __unicode__(self):
        return '{} / {} ({})'.format(self.name, self.phone, unicode(self.datetime))
