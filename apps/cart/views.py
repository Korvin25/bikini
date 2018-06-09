# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, View
from django.http import HttpResponseRedirect

from ..catalog.models import Attribute, GiftWrapping, SpecialOffer
from ..core.templatetags.core_tags import to_int_or_float
from ..geo.models import Country
from .cart import Cart
from .models import DeliveryMethod, PaymentMethod, CartItem, CertificateCartItem


class CartView(TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        self.cart = Cart(self.request)
        cart_items = self._get_cart_items()
        certificate_items = self._get_certificate_items()
        self._color_stuff(cart_items)

        if not (cart_items.exists() or certificate_items.exists()):
            self.cart.clear()
            cart_items = CartItem.objects.none()
            certificate_items = CertificateCartItem.objects.none()

        shipping_data = {
            'country': 132,  # Россия
            'city': '',
            'address': '',
            'phone': '',
            'name': '',
            'email': '',
            'payment_method_id': None,
            'delivery_method_id': None,
        }
        profile = self.request.user
        if profile.is_authenticated():
            shipping_data.update(profile.shipping_data)
        for k, v in shipping_data.items():
            if getattr(self.cart.cart, k, None):
                shipping_data[k] = getattr(self.cart.cart, k)

        delivery_methods = DeliveryMethod.objects.prefetch_related('payment_methods').filter(
            is_enabled=True, payment_methods__isnull=False,
        ).distinct()
        payment_methods = PaymentMethod.objects.prefetch_related('delivery_methods').filter(
            is_enabled=True, delivery_methods__isnull=False,
        ).distinct()

        context = {
            'cart_items': cart_items,
            'certificate_items': certificate_items,
            'with_color': self.with_color,
            'color_attribute': self.color_attribute,
            'with_gift_wrapping': True,
            'gift_wrapping_price': to_int_or_float(GiftWrapping.get_price() or 0),
            'countries': Country.objects.values('id', 'title'),
            'shipping_data': shipping_data,
            'specials': SpecialOffer.get_offers(),
            'random_str': str(uuid.uuid4()).replace('-', ''),
            'delivery_methods': delivery_methods,
            'payment_methods': payment_methods,
        }
        context.update(super(CartView, self).get_context_data(**kwargs))
        return context

    def _get_cart_items(self):
        cart = self.cart
        cart_items = cart.cart.cartitem_set.all().select_related('product', 'option')
        for item in cart_items:
            if item.count == 0:
                item.delete()
        cart_items = cart.cart.cartitem_set.all().select_related('product', 'option')
        return cart_items

    def _get_certificate_items(self):
        cart = self.cart
        certificate_items = cart.cart.certificatecartitem_set.all().select_related('certificate')
        return certificate_items

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


class CartGetDiscountView(View):

    def get(self, request, *args, **kwargs):
        profile = request.user
        offer_id = kwargs.get('pk')
        redirect_url = reverse('cart')

        if not profile.is_anonymous() and profile.can_get_discount:
            try:
                special_offer = SpecialOffer.get_offers().get(id=offer_id)
            except (ValueError, SpecialOffer.DoesNotExist) as e:
                pass
            else:
                discount_code = profile.get_discount_code()
                redirect_url = special_offer.get_offer_url(discount_code=discount_code)

        return HttpResponseRedirect(redirect_url)
