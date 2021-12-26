# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.core.management.base import BaseCommand

from apps.cart.models import Cart as CartModel
from apps.cart.yoo_utils import yoo_update_cart_with_payment


l = logging.getLogger('yookassa')


class Command(BaseCommand):
    help = 'Updating yookassa carts with pending status'

    def handle(self, *args, **options):
        carts = CartModel.objects.filter(yoo_status='pending')
        carts_count = carts.count()
        self.stdout.write('Carts count: {}'.format(carts_count))
        if carts_count:
            self.stdout.write('Updating...')
            l.info('-------')
            l.info('Updating pending carts (count {})'.format(carts_count))
            for cart in carts:
                yoo_update_cart_with_payment(cart, logger=l)
            l.info('  done!')
        self.stdout.write(self.style.SUCCESS('Done!'))
