# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from crequest.middleware import CrequestMiddleware


class Country(models.Model):
    title = models.CharField(_('Название'), max_length=255)
    order = models.IntegerField(_('Порядок'), default=10)

    class Meta:
        app_label = 'geo'
        ordering = ['order', 'title', ]
        verbose_name = _('страна')
        verbose_name_plural = _('страны')

    def __unicode__(self):
        return self.title


class City(models.Model):
    country = models.ForeignKey(Country, verbose_name=_('Страна'))
    title = models.CharField(_('Название'), max_length=255)
    order = models.IntegerField(_('Порядок'), default=10)

    class Meta:
        app_label = 'geo'
        ordering = ['country', 'order', 'title', ]
        verbose_name = _('город')
        verbose_name_plural = _('города')

    def __unicode__(self):
        return self.title
