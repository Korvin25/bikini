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

    def update(self, *args, **kwargs):
        cart = self.cart
        for k, v in kwargs.items():
            setattr(cart, k, v)
        cart.save()
        return cart

    def set(self, product_id, hash, option_id, item_id, count, **kwargs):
        Item = models.CartItem
        item = None

        with_discount = bool(kwargs.get('discount', 0))
        if with_discount:
            items_with_discount = self.cart.cartitem_set.filter(discount__gt=0)
            if items_with_discount.count():
                keep_discount = False
                for i in items_with_discount:
                    if i.product_id == product_id and i.hash == hash:
                        keep_discount = True
                        break
                if keep_discount is False:
                    kwargs['discount'] = 0

        if product_id and option_id:
            try:
                item = Item.objects.filter(
                    cart=self.cart,
                    product_id=product_id,
                    hash=hash,
                    # option_id=option_id,
                    discount=kwargs.get('discount', 0),
                ).first()
                if not item:
                    item = Item(
                        cart=self.cart,
                        product_id=product_id,
                        hash=hash,
                        option_id=option_id,
                        discount=kwargs.get('discount', 0),
                    )
            except ValueError:
                pass

        elif item_id:
            try:
                item = Item.objects.get(
                    cart=self.cart,
                    id=item_id,
                )
            except (Item.DoesNotExist, ValueError) as e:
                pass

        if not item:
            return False

        if option_id:
            item.option_id = option_id
        item.count = count
        for k, v in kwargs.items():
            setattr(item, k, v)
        item.save()
        item.set_hash()
        self.cart.save()
        return item

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

    def set_certificate(self, certificate_id, **kwargs):
        Item = models.CertificateCartItem
        item = None

        try:
            item = Item.objects.get(
                cart=self.cart,
                certificate_id=certificate_id,
            )
        except Item.DoesNotExist:
            item = Item(
                cart=self.cart,
                certificate_id=certificate_id,
                **kwargs
            )

        if not item:
            return False

        for k, v in kwargs.items():
            setattr(item, k, v)
        item.save()
        self.cart.save()
        return item

    def remove_certificate(self, item_id):
        Item = models.CertificateCartItem
        try:
            item = Item.objects.get(
                cart=self.cart,
                id=item_id,
            )
            item.delete()
            self.cart.save()

        except Item.DoesNotExist:
            pass

    def count(self):
        return self.cart.count()

    def summary(self):
        return self.cart.show_summary()

    @property
    def number(self):
        return self.cart.number

    def clear(self):
        for item in self.cart.cartitem_set.all():
            item.delete()
        for item in self.cart.certificatecartitem_set.all():
            item.delete()
        self.cart.delete()
