# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crequest.middleware import CrequestMiddleware


def get_current_lang():
    try:
        request = CrequestMiddleware.get_request()
        return request.LANGUAGE_CODE
    except:
        return 'ru'
