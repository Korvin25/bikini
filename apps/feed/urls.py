# -*- coding: utf-8 -*-
import apps.feed.views as views_rss
from django.conf.urls import url

urlpatterns = [
    url(r'^yandex.xml$', views_rss.yandex_rss, name='yandex_rss'),
    url(r'^aliexpress.xml$', views_rss.aliexpress_rss, name='aliexpress_rss'),
    url(r'^ozon_update.xml$', views_rss.ozon_rss, name='ozon_rss'),
]
