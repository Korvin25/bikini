# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import retailcrm
from django.core.management.base import BaseCommand

from apps.cart.models import Cart as CartModel


class Command(BaseCommand):
    help = 'Отправить все заказы в срм'

    def handle(self, *args, **options):
        carts = CartModel.objects.prefetch_related('profile', 'cartitem_set', 'certificatecartitem_set').filter(checked_out=True)[:5]

        client = retailcrm.v5('https://bikinimini.retailcrm.ru', 'WauoN85ORs7QLJe0SFvjC4GzZpYXoIu1')
        site = 'bikinimini'

        for cart in carts:
            items = cart.cart_items

            if items:
                order = {
                    'orderMethod': 'shopping-cart',
                    'firstName': cart.profile.name,
                    'phone': cart.profile.phone,
                    'email': cart.profile.email,
                    'createdAt': cart.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': get_status(cart.payment_status),
                    'delivery': {
                        'code':cart.delivery_method.code_retailcrm,
                        'address': {
                            'index': cart.postal_code,
                            'countryIso': cart.country.title,
                            'city': cart.city,
                            'street': cart.address,
                        }
                    },
                    'items': [
                                {
                                    # 'externalId': item.product.vendor_code,
                                    'article': item.product.vendor_code,
                                    'initialPrice': float(item.option.price),
                                    'productName': item.option.title,
                                    'quantity': item.count,
                                    'comment': 'Подарочная упаковка: {}'.format('Да' if item.with_wrapping else 'Нет')
                                }
                                for item in items
                            ]
                    }

                # print(order)
                # print(cart.id)
                result = client.order_create(order, site)

                print(result.get_response())

                if result.is_successful():
                    cart.retailcrm = result.get_response()['id']
                    cart.save()


def get_status(status):
    STATUS = {
        'pending': 'novyi',
        'succeeded': 'paid',
        'canceled': 'novyi',
        'error': 'cancel-other',
        'processed': 'ozhidaet-oplatu', 
        'in-progress': 'ozhidaet-oplatu',
        'completed': 'paid',
        'paid': 'paid',
        'cancelled': 'cancel-other',
        'denied': 'cancel-other',
        'refused': 'cancel-other',
        'declined': 'оcancel-other',
        'cleared': 'cancel-other',
        'failed': 'cancel-other',
        'expired': 'исcancel-otherек',
        'refunded': 'cancel-other',
        'partially_refunded': 'cancel-other',
        'reversed': 'cancel-other',
        'canceled_reversal': 'cancel-other',
        'rewarded': 'cancel-other',
        'unclaimed': 'cancel-other',
        'uncleared': 'cancel-other',
        'voided': 'cancel-other',
        'error': 'cancel-other',
    }
    try:
        return STATUS[status]
    except:
        return 'new'