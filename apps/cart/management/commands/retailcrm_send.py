# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from apps.cart.models import Cart as CartModel
from apps.cart.retailcrm_utils import send_retailcrm


class Command(BaseCommand):
    help = 'Отправить все заказы в срм'

    def handle(self, *args, **options):
        carts = CartModel.objects.prefetch_related('profile', 'cartitem_set', 'certificatecartitem_set').filter(checked_out=True, retailcrm__isnull=True)
        # carts = CartModel.objects.prefetch_related('profile', 'cartitem_set', 'certificatecartitem_set').filter(checked_out=True, retailcrm='Old Cart')
        print('-----Start-----')
        print('carts: {}'.format(len(carts)))
        send_retailcrm(list(carts))
        print('-----Finish-----Count: {}'.format(len(carts)))