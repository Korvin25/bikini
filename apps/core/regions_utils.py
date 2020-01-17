# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crequest.middleware import CrequestMiddleware


def get_region_code(request=None):
    
    return 


def region_field(obj, field_name='title', request=None, region_code=None, add_suffix=False, use_default=True):
    request = request or CrequestMiddleware.get_request()
    region_code = region_code or getattr(request, 'region_code', None)

    _value = getattr(obj, field_name) or ''

    if region_code:
        region_field_name = '{}_{}'.format(field_name, region_code)
        _region_value = getattr(obj, region_field_name, '')

        if _region_value:
            _value = _region_value
        elif use_default is False:
            _value = ''
        elif _value and add_suffix is True:
            seo_suffix = getattr(request, 'region_seo_suffix', '')
            _value = '{} {}'.format(_value, seo_suffix)

    return _value


def get_region_seo_suffix(request=None):
    request = request or CrequestMiddleware.get_request()
    seo_suffix = getattr(request, 'region_seo_suffix', '')
    return seo_suffix
