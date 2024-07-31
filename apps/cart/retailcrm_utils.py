# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import retailcrm
from uuslug import slugify

from ..catalog.models import AttributeOption, GiftWrapping


def send_retailcrm(carts):
    client = retailcrm.v5('https://bikinimini.retailcrm.ru', 'WauoN85ORs7QLJe0SFvjC4GzZpYXoIu1')
    site = 'bikinimini'
    
    if not isinstance(carts, list):
        carts = [carts]

    for cart in carts:
        print('cart: {}'.format(cart.id))
        items = cart.cart_items
        print('retailcrm: {}'.format(cart.retailcrm))
        if items:
            if cart.retailcrm:
                order = get_order(cart, items, cart.retailcrm)
                result = client.order_edit(order, 'externalId', site)
                print(result.get_response())
                if result.is_successful():
                    retailcrm_id = result.get_response()['id']
                    print(retailcrm_id)
                    cart.retailcrm = retailcrm_id
                    cart.save()
                else:
                    result = client.order_create(order, site)
                    if result.is_successful():
                        retailcrm_id = result.get_response()['id']
                        print(retailcrm_id)
                        cart.retailcrm = retailcrm_id
                        cart.save()
                    else:
                        print(order['payments'][0]['status'])
                        print(result.get_response())
                
            else:
                order = get_order(cart, items)
                result = client.order_create(order, site)

                if result.is_successful():
                    retailcrm_id = result.get_response()['id']
                    print(retailcrm_id)
                    cart.retailcrm = retailcrm_id
                    cart.save()
                else:
                    print(order['payments'][0]['status'])
                    print(result.get_response())


def get_status(status):
    STATUS = {
        'pending': 'novyi',
        'succeeded': 'paid',
        'canceled': 'novyi',
        'completed': 'paid',
        'paid': 'paid',
        'error': 'oshibka',
    }
    try:
        return STATUS[status]
    except:
        return 'novyi'


def get_status_payments(status):
    STATUS = {
        'pending': 'not-paid',
        'succeeded': 'paid',
        'canceled': 'not-paid',
        'completed': 'paid',
        'paid': 'paid',
    }
    try:
        return STATUS[status]
    except:
        return 'not-paid'


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

def get_customer_comment(comment, address):
    if len(address) < 255:
        return comment
    else:
        return u'Комментарий клиента: "{}". Адрес: {}'.format(comment, address)

def get_order(cart, items, uid_type=None):
    order = {
        'externalId': str(cart.id),
        'orderMethod': 'shopping-cart',
        'firstName': cart.profile.name,
        'phone': cart.profile.phone,
        'email': cart.profile.email,
        'createdAt': cart.checkout_date.strftime('%Y-%m-%d %H:%M:%S') if cart.checkout_date else cart.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
        'status': get_status(cart.payment_status),
        'customerComment': get_customer_comment(cart.additional_info, cart.address),
        'managerComment': 'На сайте: https://bikinimini.ru/admin/cart/cart/{}/change/'.format(cart.id),
        'delivery': {
            'cost': float(cart.delivery_method.price_rub),
            'code': cart.delivery_method.code_retailcrm,
            'address': {
                'index': cart.postal_code,
                'countryIso': cart.country.title,
                'city': cart.city,
                'street': cart.address if len(cart.address) < 255 else u'Адрес в поле "Комментрий клиента", так-как на сайте заполнен адресс длинее 255 символов',
            }
        },
        'payments': [{
            'amount': float(cart.summary_c),
            'type': cart.payment_method.code_retailcrm,
            'status': get_status_payments(cart.payment_status),
            # 'paidAt': cart.payment_date.strftime('%Y-%m-%d %H:%M:%S') if cart.payment_date else '',
        }],
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

    if uid_type:
        order['externalId'] = str(cart.id)
        order['by'] = 'externalId'

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

    return order
