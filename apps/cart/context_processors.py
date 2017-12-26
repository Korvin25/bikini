# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .cart import Cart


def cart(request):
    cart = Cart(request)
    basket = cart.cart
    # basket_data = cart.get_basket()

    return {
        'cart': cart,
        'basket': basket,
        # 'basket_data': basket_data,
    }
