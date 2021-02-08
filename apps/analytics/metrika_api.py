# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

import requests

from .conf import YM_COUNTER, YANDEX_OAUTH_TOKEN, YANDEX_API_BASE_URL


l = logging.getLogger('analytics.api')


def get_traffic_source(client_id):
    ym_source = None
    ym_source_detailed = None

    _args = [YANDEX_API_BASE_URL, YM_COUNTER, client_id]
    url = '{}?ids={}&period=week&metrics=ym:s:visits&dimensions=ym:s:firstTrafficSource,ym:s:firstSourceEngineName&filters=ym:s:clientID=={}'.format(*_args)

    try:
        r = requests.get(url, headers={'Authorization': 'OAuth {}'.format(YANDEX_OAUTH_TOKEN)})
        r.raise_for_status()
        response = r.json()

        source_data = response['data'][0]['dimensions']
        ym_source = source_data[0].get('id')
        ym_source_detailed = source_data[1].get('name')

    except Exception as exc:
        print exc

    return ym_source, ym_source_detailed
