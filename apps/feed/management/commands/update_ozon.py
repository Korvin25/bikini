# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.conf import settings
from apps.catalog.models import Product
from apps.feed.ozon_seller import OzonSeller


class Command(BaseCommand):
    help = u'Обновить и добавить товары на Озон'

    def handle(self, *args, **options):

        ozon_api = OzonSeller(settings.OZON_CLIENT_ID, settings.OZON_API_KEY)

        for product in Product.objects.filter(show_at_yandex=True):
            ozon_api.update_product(product)
