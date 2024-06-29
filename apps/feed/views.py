# -*- coding: utf-8 -*-
from apps.catalog.models import Product
from apps.feed.utils import GenerateFeed, html_unescape
from django.http import HttpResponse
from django.conf import settings


PARAMS = {
    'name': settings.SITE_TITLE,
    'company': settings.SITE_COMPANY,
    'url': settings.SITE_LINK,
    'platform': settings.SITE_PLATFORM,
    'version': settings.SITE_VERSION,
    'agency': settings.SITE_DESC,
    'email': settings.SITE_EMAIL,
    'weight': settings.WEIDHT, 
    'dimensions': settings.DIMENSIONS,
}


def retailcrm_rss(request):

    feed = GenerateFeed(**PARAMS)

    for product in Product.objects.filter(retailcrm=True):
        feed.create_retailcrm_item(product)

    return HttpResponse(html_unescape(feed.to_xml()), content_type='text/xml')
    

def yandex_rss(request):

    feed = GenerateFeed(**PARAMS)

    for product in Product.objects.filter(show_at_yandex=True):
        feed.create_yandex_item(product)

    return HttpResponse(html_unescape(feed.to_xml()), content_type='text/xml')


def aliexpress_rss(request):

    feed = GenerateFeed(**PARAMS)

    for product in Product.objects.filter(show_at_yandex=True):
        feed.create_aliexpress_item(product)
    
    return HttpResponse(html_unescape(feed.to_xml()), content_type='text/xml')


def ozon_rss(request):

    feed = GenerateFeed(**PARAMS)

    for product in Product.objects.filter(show_at_yandex=True):
        feed.create_ozon_item(product)
    
    return HttpResponse(html_unescape(feed.to_xml()), content_type='text/xml')
