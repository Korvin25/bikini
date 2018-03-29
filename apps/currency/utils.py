# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crequest.middleware import CrequestMiddleware

from .conf import DEFAULT_CURRENCY, SESSION_CURRENCY_KEY, VALID_CURRENCIES


def get_currency(request=None):
    if request is None:
        request = CrequestMiddleware.get_request()

    currency = DEFAULT_CURRENCY
    if request.session:
        currency = request.session.get(SESSION_CURRENCY_KEY, DEFAULT_CURRENCY)

    return currency


def set_currency(request, currency):
    if request.session and currency in VALID_CURRENCIES:
        request.session[SESSION_CURRENCY_KEY] = currency
    return request


def currency_price(obj, field_name='price', request=None, currency=None):
    currency = currency or get_currency(request=request)
    key = '{}_{}'.format(field_name, currency)
    price = (getattr(obj, key) if not isinstance(obj, dict)
             else obj.get(key))
    return price
