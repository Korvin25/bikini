# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import models


CART_ID = 'CART-ID'


class ItemDoesNotExist(Exception):
    pass


class Cart:

    def __init__(self, request):
        cart_id = request.session.get(CART_ID)
        if cart_id:
            try:
                cart = models.Cart.objects.get(id=cart_id, checked_out=False)
            except models.Cart.DoesNotExist:
                cart = self.new(request)
        else:
            cart = self.new(request)
        self.cart = cart

    def new(self, request):
        if request.user.is_authenticated():
            cart = models.Cart(profile=request.user)
        else:
            cart = models.Cart()
        cart.save()
        request.session[CART_ID] = cart.id
        return cart

    def set(self, product_id, option_id, count, **kwargs):
        Item = models.CartItem
        try:
            item = Item.objects.get(
                cart=self.cart,
                product_id=product_id,
                option_id=option_id,
            )
        except Item.DoesNotExist:
            item = Item(
                cart=self.cart,
                product_id=product_id,
                option_id=option_id,
            )

        item.count = count
        for k, v in kwargs.items():
            setattr(item, k, v)
        item.save()
        self.cart.save()
        return True

    def remove(self, item_id):
        Item = models.CartItem
        try:
            item = Item.objects.get(
                cart=self.cart,
                id=item_id,
            )
            item.delete()
            self.cart.save()

        except Item.DoesNotExist:
            # raise ItemDoesNotExist
            pass

    def count(self):
        return self.cart.count()

    def summary(self):
        return self.cart.show_summary()

    def clear(self):
        for item in self.cart.cartitem_set.all():
            item.delete()
        self.cart.delete()
