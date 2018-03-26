# -*- coding: utf-8 -*-
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# (http://stackoverflow.com/a/36081249)
from .celery import app as celery_app
