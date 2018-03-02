# -*- coding: utf-8 -*-
from __future__ import unicode_literals


RUB = 'rub'
EUR = 'eur'
USD = 'usd'
VALID_CURRENCIES = {RUB, EUR, USD}

RU = 'RU'
EU = 'EU'

COUNTRY_CURRENCY_DICT = {
    RU: RUB,
    EU: EUR,
}

DEFAULT_CURRENCY = RUB
COUNTRY_DEFAULT_CURRENCY = USD

SESSION_CURRENCY_KEY = 'currency'
SESSION_COUNTRY_CODE = 'country_code'

IPDATA_UNAVAILABLE_REDIS_KEY = 'bikini.ipdata.unavailable'
IPDATA_API_URL = 'https://api.ipdata.co/'
