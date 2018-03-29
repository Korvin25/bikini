# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from apps.catalog.models import Product, ProductOption
from apps.currency.utils import currency_price


def get_wishlist_from_request(request):
    profile = request.user
    wishlist = request.session.get('wishlist', []) if profile.is_anonymous() else profile.wishlist
    wishlist = [item for item in wishlist if item.get('option_id') and item.get('hash') and item.get('price_rub')]
    for item in wishlist:
        item['price'] = currency_price(item, request=request)
    return wishlist


def get_wishlist_item_prices(product_id, option_id, extra_products):
    product = Product.objects.get(id=product_id)
    option = ProductOption.objects.get(id=option_id)

    option_price_rub = option.price_rub
    option_price_eur = option.price_eur
    option_price_usd = option.price_usd

    extra_price_rub = Decimal(0.0)
    extra_price_eur = Decimal(0.0)
    extra_price_usd = Decimal(0.0)
    if extra_products:
        extra_products = product.extra_products.filter(extra_product_id__in=extra_products.keys())
        prices = extra_products.values('price_rub', 'price_eur', 'price_usd')
        extra_price_rub = sum([price['price_rub'] for price in prices])
        extra_price_eur = sum([price['price_eur'] for price in prices])
        extra_price_usd = sum([price['price_usd'] for price in prices])

    price_rub = option_price_rub + extra_price_rub
    price_eur = option_price_eur + extra_price_eur
    price_usd = option_price_usd + extra_price_usd

    return {
        'rub': price_rub,
        'eur': price_eur,
        'usd': price_usd,
    }
