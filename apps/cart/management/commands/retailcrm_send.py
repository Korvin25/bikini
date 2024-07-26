# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import retailcrm
from uuslug import slugify
from django.core.management.base import BaseCommand

from apps.cart.models import Cart as CartModel
from apps.cart.retailcrm_utils import send_retailcrm
from apps.catalog.models import AttributeOption, GiftWrapping


class Command(BaseCommand):
    help = 'Отправить все заказы в срм'

    def handle(self, *args, **options):
        carts = CartModel.objects.prefetch_related('profile', 'cartitem_set', 'certificatecartitem_set').filter(checked_out=True)[:100]

        send_retailcrm(carts, command=True)