# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from redis import StrictRedis


def get_redis_database():
    return StrictRedis(
        host = settings.REDIS_HOST,
        port = settings.REDIS_PORT,
        db = settings.REDIS_DB,
        # socket_timeout = settings.REDIS_SOCKET_TIMEOUT,
    )

redis = get_redis_database()
