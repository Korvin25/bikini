# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView

from ..catalog.models import Attribute, GiftWrapping
from ..core.templatetags.core_tags import to_int_plus
from ..geo.models import Country
from .cart import Cart
from .models import CartItem


class CartView(TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        cart_items = self._get_cart_items()
        self._color_stuff(cart_items)

        shipping_data = {
            'country': 132,  # Россия
            'city': '',
            'address': '',
            'phone': '',
            'name': '',
        }
        profile = self.request.user
        if profile.is_authenticated():
            shipping_data.update(profile.shipping_data)

        context = {
            'cart_items': cart_items,
            'with_color': self.with_color,
            'color_attribute': self.color_attribute,
            'with_gift_wrapping': True,
            'gift_wrapping_price': to_int_plus(GiftWrapping.get_price() or 0),
            'countries': Country.objects.values('id', 'title'),
            'shipping_data': shipping_data,
        }
        context.update(super(CartView, self).get_context_data(**kwargs))
        return context

    def _get_cart_items(self):
        cart = Cart(self.request)
        cart_items = cart.cart.cartitem_set.all().select_related('product')
        for item in cart_items:
            if item.count == 0:
                item.delete()
        cart_items = cart.cart.cartitem_set.all().select_related('product')
        if not cart_items.exists():
            cart.clear()
            cart_items = CartItem.objects.none()
        return cart_items

    def _color_stuff(self, cart_items):
        with_color = False
        color_attribute = None

        if cart_items.exists():
            for attrs in cart_items.values_list('attrs', flat=True):
                if 'color' in attrs.keys():
                    with_color = True
                    break
            if with_color:
                color_attribute = Attribute.objects.filter(slug='color').first()
                if not color_attribute:
                    with_color = False

        self.with_color = with_color
        self.color_attribute = color_attribute
