# -*- coding: utf-8 -*-
from __future__ import unicode_literals


RUB_CODE = 'rub'
EUR_CODE = 'eur'
USD_CODE = 'usd'
VALID_CURRENCIES = {RUB_CODE, EUR_CODE, USD_CODE}

RU_CODE = 'RU'
EU_CODE = 'EU'

COUNTRY_CURRENCY_DICT = {
    RU_CODE: RUB_CODE,
    EU_CODE: EUR_CODE,
}

DEFAULT_CURRENCY = RUB_CODE
COUNTRY_DEFAULT_CURRENCY = USD_CODE

SESSION_CURRENCY_KEY = 'currency'
SESSION_COUNTRY_CODE = 'country_code'

IPDATA_UNAVAILABLE_REDIS_KEY = 'bikini.ipdata.unavailable'
IPDATA_API_URL = 'https://api.ipdata.co/'
