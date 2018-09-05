# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


ENABLE_METRICS = getattr(settings, 'ENABLE_METRICS', False)
YM_COUNTER = getattr(settings, 'YM_COUNTER', None)
YANDEX_OAUTH_TOKEN = getattr(settings, 'YANDEX_OAUTH_TOKEN', None)
YANDEX_API_BASE_URL = 'https://api-metrika.yandex.ru/stat/v1/data'

SESSION_YM_CLIENT_ID_KEY = 'ym_client_id'
SESSION_YM_CLIENT_DT_KEY = 'ym_client_dt'
