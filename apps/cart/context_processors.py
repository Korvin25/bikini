# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .cart import Cart


def cart(request):
    if request.path.startswith('/admin/'):
        return {}

    cart = Cart(request)
    basket = cart.cart
    # basket_data = cart.get_basket()

    profile = request.user
    if profile.is_authenticated() and not basket.profile_id:
        basket.profile = profile
        basket.save()

    return {
        'cart': cart,
        'basket': basket,
        # 'basket_data': basket_data,
    }
