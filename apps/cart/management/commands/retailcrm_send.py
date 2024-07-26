# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import retailcrm
from uuslug import slugify
from django.core.management.base import BaseCommand

from apps.cart.models import Cart as CartModel
from apps.catalog.models import AttributeOption, GiftWrapping


class Command(BaseCommand):
    help = 'Отправить все заказы в срм'

    def handle(self, *args, **options):
        carts = CartModel.objects.prefetch_related('profile', 'cartitem_set', 'certificatecartitem_set').filter(checked_out=True)[:3]

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
                        'cost': float(cart.delivery_method.price_rub),
                        'code': cart.delivery_method.code_retailcrm,
                        'address': {
                            'index': cart.postal_code,
                            'countryIso': cart.country.title,
                            'city': cart.city,
                            'street': cart.address,
                        }
                    },
                    'payments': {
                        'amount': float(cart.summary_c),
                        # 'type': cart.payment_method.code_retailcrm,
                        'status': get_status_payments(cart.payment_status),
                    },
                    'items': [
                        {
                            'offer': {
                                'externalId': get_article(item),
                            },
                            'properties': get_properties(item),
                            'article': get_article(item),
                            'initialPrice': float(item.option_price_c),
                            'productName': item.option.title,
                            'quantity': item.count,
                            'discountManualAmount': float((item.option_price_c * item.discount)/100),
                        }
                        for item in items
                    ]
                }

                with_wrapping = {
                    'initialPrice': float(GiftWrapping.objects.first().price_rub),
                    'productName': u'Подарочная упаковка',
                    'quantity': 0,
                }

                for item in items:
                    if item.with_wrapping:
                        with_wrapping['quantity'] += 1

                if with_wrapping['quantity'] > 0:
                    order['items'].append(with_wrapping)


                result = client.order_create(order, site)
                print(result.get_response())
                if result.is_successful():
                    retailcrm_id = result.get_response()['id']
                    print(retailcrm_id)
                    cart.retailcrm = retailcrm_id
                    cart.save()


def get_status(status):
    STATUS = {
        'pending': 'novyi',
        'succeeded': 'paid',
        'canceled': 'novyi',
        'completed': 'paid',
        'paid': 'paid',
    }
    try:
        return STATUS[status]
    except:
        return 'novyi'


def get_status_payments(status):
    STATUS = {
        'pending': 'Не оплачен',
        'succeeded': 'Оплачен',
        'canceled': 'Не оплачен',
        'completed': 'Оплачен',
        'paid': 'Оплачен',
    }
    try:
        return STATUS[status]
    except:
        return 'Не оплачен'


def get_properties(item):
    properties = [
            {
                'name': u'Подарочная упаковка',
                'value': u'Да' if item.with_wrapping else u'Нет',
            },
        ]
    for key, value in item.attrs.items():
        atribute = AttributeOption.objects.get(pk=value)
        properties.append(
              {
                'name': atribute.attribute.admin_title,
                'value': atribute.title,
            }
        )
    
    return properties


def get_article(item):
    combination_id = [value for key, value in item.attrs.items()]
    combinations = AttributeOption.objects.filter(pk__in=combination_id)
    letters = ['{}-{}'.format(i.attribute.slug, i.title) for i in combinations]
    letters = '-'.join(letters)
    letters = item.product.vendor_code + '-' + letters
    letters = slugify(letters)
    return letters