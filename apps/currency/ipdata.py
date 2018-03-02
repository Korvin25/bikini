# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ipware.ip import get_real_ip
import requests

from apps.core.redis_utils import redis
from .conf import RU, EU, IPDATA_UNAVAILABLE_REDIS_KEY, IPDATA_API_URL


class RequestError(BaseException):
    pass


def _request(url, method='get', data=None, headers={'Accept': 'application/json'}):
    allow_redirects = False

    try:
        response = requests.request(url=url, method=method, data=data, headers=headers, allow_redirects=allow_redirects)
    except requests.RequestException as err:
        raise RequestError(err)

    if not response.status_code == 200:
        raise RequestError('response status code is not 200 (status_code={})'.format(response.status_code))

    try:
        return response.json()
    except Exception as exc:
        raise RequestError('response is not json')


def get_country_data(request):
    country_data = {
        'country_code': RU,
        'for_currency': RU,
        'is_eu': False,
    }

    if not redis.get(IPDATA_UNAVAILABLE_REDIS_KEY):
        ip = get_real_ip(request)
        if ip:
            try:
                url = '{}{}'.format(IPDATA_API_URL, ip)
                data = _request(url)
            except RequestError as err:
                redis.setex(self.IPDATA_UNAVAILABLE_REDIS_KEY, 1800, 'true')
                # TODO: logging
            else:
                country_data['country_code'] = data['country_code']
                country_data['for_currency'] = EU if data['is_eu'] else data['country_code']
                country_data['is_eu'] = data['is_eu']

    return country_data
