# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import yandex_rss

urlpatterns = [
    url(r'^yandex.xml$', yandex_rss, name='yandex_rss'),
]
