# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crequest.middleware import CrequestMiddleware


def get_region_code(request=None):
    request = request or CrequestMiddleware.get_request()
    return request.region_code


def region_field(obj, field_name='title', request=None, region_code=None):
    region_code = region_code or get_region_code(request)
    _value = getattr(obj, field_name)

    if region_code:
        region_field_name = '{}_{}'.format(field_name, region_code)
        _value = getattr(obj, region_field_name, field_name) or _value

    return _value
