# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.deprecation import MiddlewareMixin

from .conf import COUNTRY_CURRENCY_DICT, COUNTRY_DEFAULT_CURRENCY, SESSION_CURRENCY_KEY, SESSION_COUNTRY_CODE
from .ipdata import get_country_data


class CurrencyMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user_agent.is_bot:
            return None

        if request.session and not request.session.get(SESSION_CURRENCY_KEY):
            country_data = get_country_data(request)
            currency = COUNTRY_CURRENCY_DICT.get(country_data['for_currency'], COUNTRY_DEFAULT_CURRENCY)

            request.session[SESSION_CURRENCY_KEY] = currency
            request.session[SESSION_COUNTRY_CODE] = country_data['country_code']
        return None
