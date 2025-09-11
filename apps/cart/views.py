# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
import json
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View, CreateView

from .retailcrm_utils import send_retailcrm

from ..catalog.models import Attribute, GiftWrapping, SpecialOffer, Product
from ..core.templatetags.core_tags import to_int_or_float
from ..geo.models import Country
from ..lk.email import email_admin
from ..settings.models import Settings
from .api.robokassa import generate_payment_link
from .api.views import CheckCartMixin
from .cart import Cart
from .forms import OneClickForm
from .models import DeliveryMethod, PaymentMethod, CartItem, CertificateCartItem


class OneClickCreateView(CheckCartMixin, CreateView):
    model = Cart
    form_class = OneClickForm

    def form_valid(self, form):
        
        product = get_object_or_404(Product, pk=self.request.POST.get('product_id'))
        currency = self.request.POST.get('product_currency', 'rub')
        CURRENCY = {
            'rub': 'RUB',
            'eur': 'EUR',
            'usd': 'USD'
        }

        self.object = form.save(commit=False)
        self.object.is_one_click = True
        self.object.currency = currency
        self.object.save()

        cart_item = CartItem.objects.create(
            cart=self.object,
            product=product,
            option=product.options.first(),
            discount=0 if not product.is_on_sale else product.sale_percent,
            count=1
        )
        cart_item.update_price()

        self.object.get_summary()
        self.object.save()

        self.check_cart(cart_item)

        receipt = {
            "items": [
                {
                    "name": product.title,
                    "quantity": 1,
                    "sum": float(self.object.summary),
                    "tax": "none"
                }
            ]
        }
        
        payment_url = generate_payment_link(
            merchant_login=settings.ROBOKASSA_LOGIN,
            merchant_password_1=settings.ROBOKASSA_PASSWORD_1,
            cost=float(self.object.summary),
            number=self.object.id,
            description='Быстрый заказ #{}'.format(self.object.id),
            email=None,
            currency=CURRENCY[currency],
            receipt=json.dumps(receipt),
            is_test=0,
        )

        self.object.payment_method = PaymentMethod.objects.get(is_enabled=True, payment_type='robokassa')
        self.object.robokassa_id = self.object.id
        self.object.robokassa_status = 'pending'
        self.object.robokassa_url = payment_url.decode('utf-8')
        self.object.checked_out = True
        self.object.checkout_date = timezone.now()
        self.object.save()

        admin_send_one_click_order_email(self.object, status='NEW')
        send_retailcrm(self.object)

        return JsonResponse({'payment_url': payment_url})

    def form_invalid(self, form):
        return JsonResponse({'errors': form.errors}, status=400)


def admin_send_one_click_order_email(obj, **kwargs):
    status = kwargs.get('status', 'NEW')
    subject = '[OneClick Order {}] #{}: {}'.format(status, obj.id, obj.cart_items.first().product.title)
    email_key = 'quick_order'
    email_admin(subject, email_key, obj, settings_key='orders_email', **kwargs)


class CartView(TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        self.cart = Cart(self.request)
        self.cart.cart.save() # при обновлении всегда перещитываем корзину
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
            'postal_code': '',
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
        _update = False
        for k, v in shipping_data.items():
            cart_obj = self.cart.cart
            # получаем shipping_data из корзины
            if getattr(cart_obj, k, None):
                shipping_data[k] = getattr(cart_obj, k)
            # если данных нет (но были в профиле) - обновляем в корзине
            elif v and hasattr(cart_obj, k):
                _k = {'country': 'country_id'}.get(k, k)
                setattr(cart_obj, _k, v)
                _update = True
        if _update:
            cart_obj.save()

        # проставляем payment_method и delivery_method

        LANGUAGE_CODE = self.request.LANGUAGE_CODE or settings.LANGUAGE_CODE
        delivery_methods = DeliveryMethod.objects.prefetch_related('payment_methods').filter(
            is_enabled=True, payment_methods__isnull=False, languages__contains=LANGUAGE_CODE,
        ).distinct()
        payment_methods = PaymentMethod.objects.prefetch_related('delivery_methods').filter(
            is_enabled=True, delivery_methods__isnull=False, languages__contains=LANGUAGE_CODE,
        ).distinct()

        _update = False
        if cart_obj.delivery_method not in delivery_methods:
            cart_obj.delivery_method = None
            shipping_data['delivery_method_id'] = None
            _update = True
        if cart_obj.payment_method not in payment_methods:
            cart_obj.payment_method = None
            shipping_data['payment_method_id'] = None
            _update = True
        if _update:
            cart_obj.save()
            
        context = {
            'cart_items': cart_items,
            'certificate_items': certificate_items,
            'with_color': self.with_color,
            'color_attribute': self.color_attribute,
            'with_gift_wrapping': True,
            'gift_wrapping_price': to_int_or_float(GiftWrapping.get_price() or 0),
            'countries': Country.objects.values('id', 'title'),
            'shipping_data': shipping_data,
            'delivery_methods': delivery_methods,
            'payment_methods': payment_methods,
            'four_products_free': Settings.objects.first().four_products_free,
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
        return cart_items.filter(product__show=True)

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
            except (ValueError, SpecialOffer.DoesNotExist) as e:  # noqa
                pass
            else:
                discount_code = profile.get_discount_code()
                redirect_url = special_offer.get_offer_url(discount_code=discount_code)

        return HttpResponseRedirect(redirect_url)
