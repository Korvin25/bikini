# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import itertools
import xml.etree.ElementTree as et

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.catalog.models import AttributeOption, Product
from apps.feed.utils import GenerateFeed
from apps.feed.views import PARAMS


class Command(BaseCommand):
    help = u'Сохранить фид для срм'

    def handle(self, *args, **options):

        feed = GenerateFeed(**PARAMS)
        for product in Product.objects.filter(retailcrm=True, show=True):
            combinations_iter = itertools.product(*product.attrs.values())
            for combinations_id in combinations_iter:
                combinations = AttributeOption.objects.filter(pk__in=combinations_id)
                feed.create_retailcrm_item(product, combinations, len(combinations_iter))

    
        tree = et.ElementTree(feed.el_root)
        # Запись дерева элементов в файл
        tree.write(os.path.join(settings.STATIC_ROOT, 'retailcrm.xml'))

