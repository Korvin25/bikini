# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
import logging

from celery import shared_task

from .models import EUR, USD
from .update import update_all_prices


l = logging.getLogger('currency.tasks')


@shared_task
def update_prices(currency_name, rate, from_admin=True):
    if from_admin is True:
        l.info(''); l.info('')
    l.info('-------- updating prices task starting ({}, {})'.format(currency_name, rate))

    rate = Decimal(rate)

    try:
        update_all_prices(currency_name, rate)
    except Exception as exc:
        l.error('updating prices task error ({}, {}): {}: {}'.format(currency_name, rate, unicode(exc.__class__), unicode(exc.message)))
    else:
        l.info('updating prices task done ({}, {})'.format(currency_name, rate))


@shared_task
def update_eur_prices():
    currency_name = 'eur'
    # получаем курс?
    rate = EUR.get_rate()

    l.info(''); l.info('')
    l.info('-------- updating EUR prices periodic task starting ({}, {})'.format(currency_name, rate))
    update_prices(currency_name, rate, from_admin=False)


@shared_task
def update_usd_prices():
    currency_name = 'usd'
    # получаем курс?
    rate = USD.get_rate()

    l.info(''); l.info('')
    l.info('-------- updating USD prices periodic task starting ({}, {})'.format(currency_name, rate))
    update_prices(currency_name, rate, from_admin=False)
