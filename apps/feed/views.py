# -*- coding: utf-8 -*-
from apps.catalog.models import Product
from apps.feed.utils import GenerateFeed, html_unescape
from django.http import HttpResponse

SITE_TITLE = u'Интернет магазин мини и микро бикини от Анастасии Ивановской'
SITE_LINK = u'https://bikinimini.ru'
SITE_DESC = u'Большой выбор мини и микро бикини, миниатюрные купальники ручной работы, которые выбирают смелые и уверенные в себе представительницы прекрасного пола.'
SITE_PLATFORM = u'bikinimini'
SITE_COMPANY = u'bikinimini'
SITE_VERSION = u'1.0'
SITE_EMAIL = u'ivan@adving.ru'
WEIDHT = u'0.300'
DIMENSIONS = u'20.800/23.500/1.000'

HOST = u'https://bikinimini.ru'


PARAMS = {
    'name': SITE_TITLE,
    'company': SITE_COMPANY,
    'url': SITE_LINK,
    'platform': SITE_PLATFORM,
    'version': SITE_VERSION,
    'agency': SITE_DESC,
    'email': SITE_EMAIL,
    'weight': WEIDHT, 
    'dimensions': DIMENSIONS,
}


def yandex_rss(request):

    feed = GenerateFeed(**PARAMS)

    for product in Product.objects.filter(show_at_yandex=True):
        feed.create_yandex_item(product)

    return HttpResponse(html_unescape(feed.to_xml()), content_type='text/xml')


def aliexpress_rss(request):\

    feed = GenerateFeed(**PARAMS)

    for product in Product.objects.filter(show_at_yandex=True)[10:16]:
        feed.create_aliexpress_item(product)
    
    return HttpResponse(html_unescape(feed.to_xml()), content_type='text/xml')
