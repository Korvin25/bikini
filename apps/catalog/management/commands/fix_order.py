# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from apps.catalog.models import Product


class Command(BaseCommand):
    help = u'Обновить названия для Яндекс'

    def handle(self, *args, **options):
        i = 1
        for product in Product.objects.all():
            product.order = i
            product.save()
            i += 1
