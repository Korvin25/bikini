# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .metrika_api import get_traffic_source


def update_traffic_source(obj, ym_client_id=None):
    ym_client_id = ym_client_id or obj.ym_client_id
    if ym_client_id:
        ym_source, ym_source_detailed = get_traffic_source(ym_client_id)

    obj.ym_client_id = ym_client_id
    obj.ym_source = ym_source
    obj.ym_source_detailed = ym_source_detailed
    obj.save()
