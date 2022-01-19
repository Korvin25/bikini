# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from apps.catalog.models import Category


class Command(BaseCommand):
    help = u'Обновить названия для Яндекс'

    def handle(self, *args, **options):
        for category in Category.objects.all():
            if not category.title_yandex:
                category.title_yandex = category.title
                category.save()
