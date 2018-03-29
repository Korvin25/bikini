# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import Http404, JsonResponse
from django.views.generic import View, UpdateView
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __

from apps.catalog.models import Product
from apps.cart.cart import Cart
from apps.cart.forms import CartCheckoutForm
from apps.cart.utils import make_hash_from_cartitem
from apps.core.mixins import JSONFormMixin
from apps.core.templatetags.core_tags import to_price
from apps.currency.utils import get_currency
from apps.lk.email import admin_send_order_email, send_order_email


translated_strings = (_('Корзина пуста'), _('Неправильный формат запроса'), _('Неправильный id товара'),
                      _('Выберите способы оставки и оплаты'), _('Выберите способ доставки'), _('Выберите способ оплаты'))


class EmptyCartError(Exception):
    pass


class CheckCartMixin(object):

    def check_cart(self, cart):
        cart_items = cart.cart.cartitem_set.all()
        for item in cart_items:
            if item.count == 0:
                item.delete()
        cart_items = cart.cart.cartitem_set.all()
        certificate_items = cart.cart.certificatecartitem_set.all()
        if not (cart_items or certificate_items):
            raise EmptyCartError


class CartStepBaseView(CheckCartMixin, View):

    def dispatch(self, request, *args, **kwargs):
        self.cart = Cart(request)
        self.DATA = {}

        try:
            self.check_cart(self.cart)
        except EmptyCartError:
            data = {'result': 'error', 'error': __('Корзина пуста'), 'error_code': 'CART_EMPTY'}
            return JsonResponse(data, status=400)

        try:
            self.DATA = json.loads(request.body)
        except ValueError:
            data = {'result': 'error', 'error': __('Неправильный формат запроса')}
            return JsonResponse(data, status=400)

        return super(CartStepBaseView, self).dispatch(request, *args, **kwargs)


class Step0View(CartStepBaseView):
    """
    Проверяем на залогиненность
    """

    def post(self, request, *args, **kwargs):
        status = 200

        kw = {}
        if 'additional_info' in self.DATA:
            kw['additional_info'] = self.DATA['additional_info']

        if 'delivery_method_id' in self.DATA:
            delivery_method_id = self.DATA.get('delivery_method_id')
            if delivery_method_id not in [None, '0', 0]:
                kw['delivery_method_id'] = delivery_method_id
        if 'payment_method_id' in self.DATA:
            payment_method_id = self.DATA.get('payment_method_id')
            if payment_method_id not in [None, '0', 0]:
                kw['payment_method_id'] = payment_method_id
        if len(kw):
            self.cart.update(**kw)

        basket = self.cart.cart
        if not (basket.delivery_method or basket.payment_method):
            data = {'result': 'error', 'error': __('Выберите способы оставки и оплаты')}
            status = 400
        elif not basket.delivery_method:
            data = {'result': 'error', 'error': __('Выберите способ доставки')}
            status = 400
        elif not basket.payment_method:
            data = {'result': 'error', 'error': __('Выберите способ оплаты')}
            status = 400
        else:
            if request.user.is_anonymous():
                data = {'result': 'ok', 'popup': '#step1'}
            else:
                data = {'result': 'ok', 'popup': '#step3'}
        return JsonResponse(data, status=status)


class Step2View(CartStepBaseView):
    """
    (switched off)
    Проставляем способ доставки и оплаты
    """

    def post(self, request, *args, **kwargs):
        data = {'result': 'ok', 'popup': '#step3'}
        return JsonResponse(data)


class Step3View(JSONFormMixin, CheckCartMixin, UpdateView):
    """
    Проставляем в заказ данные для доставки + оформляем его
    """
    form_class = CartCheckoutForm
    mapping = {
        'country': 'country',
        'city': 'city',
        'address': 'address',
        'phone': 'phone',
        'name': 'name',
        'email': 'email',
        'delivery_method_id': 'delivery_method_id',
        'payment_method_id': 'payment_method_id',
    }

    def dispatch(self, request, *args, **kwargs):
        self.cart = Cart(request)

        try:
            self.check_cart(self.cart)
        except EmptyCartError:
            data = {'result': 'error', 'error': __('Корзина пуста'), 'error_code': 'CART_EMPTY'}
            return JsonResponse(data, status=400)

        return super(Step3View, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.path

    def get_object(self, queryset=None):
        return self.cart.cart

    def form_valid(self, form):
        super(Step3View, self).form_valid(form)
        cart = form.instance

        if cart.count():
            cart.checked_out = True
            cart.checkout_date = timezone.now()
            cart.currency = get_currency(self.request)
            cart.save()
            super(Step3View, self).form_valid(form)

            profile = cart.profile

            if self.request.session.get('CART_ID'):
                del self.request.session['CART_ID']

            for k in self.mapping.keys():
                key = {'country': 'country_id'}.get(k, k)
                if not getattr(profile, key, None) or key in ['delivery_method_id', 'payment_method_id']:
                    setattr(profile, key, getattr(cart, key))
                if not profile.has_email and form.cleaned_data.get('email'):
                    profile.email = form.cleaned_data['email']
                    profile.has_email = True
            profile.save()

            admin_send_order_email(cart)
            if profile and profile.has_email:
                send_order_email(profile, cart)

            count = cart.count()
            summary = cart.show_summary()
            order_number = cart.number

            if cart.has_items_with_discount:
                profile.discount_used = True
                profile.save()

            popup = '#step5' if profile.can_get_discount else '#step4'
            data = {'result': 'ok', 'popup': popup, 'count': count, 'summary': summary, 'order_number': order_number}
            return JsonResponse(data)

        else:
            data = {'result': 'error', 'error_message': __('Корзина пуста')}
            return JsonResponse(data, status=400)


class UpdateCartView(View):

    def post(self, request, *args, **kwargs):
        data = {}
        DATA = {}
        cart = Cart(request)

        try:
            DATA = json.loads(request.body)
        except ValueError:
            data = {'result': 'error', 'error': __('Неправильный формат запроса')}
            return JsonResponse(data, status=400)

        cart.update(**DATA)
        count = cart.count()
        summary = cart.summary()

        data = {'result': 'ok', 'count': count, 'summary': summary}
        return JsonResponse(data)


class CartAjaxView(View):
    """
    Обрабатываем аякс-запросы на изменение корзины: 'set', 'remove' или 'clear'
    """
    action = ''

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404

        data = {}
        error = None
        DATA = {}
        cart = Cart(request)

        if self.action == 'clear':
            cart.clear()
            data['result'] = 'ok'

        else:
            try:
                DATA = json.loads(request.body)
            except ValueError:
                data = {'result': 'error', 'error': __('Неправильный формат запроса')}
                return JsonResponse(data, status=400)

            if self.action == 'remove':
                cart.remove(item_id=DATA.get('item_id', 0))
                count = cart.count()
                summary = cart.summary()

                data = {'result': 'ok', 'count': count, 'summary': summary}

            elif self.action == 'set':
                kwargs = {}

                try:
                    product_id = DATA.get('product_id', 0)
                    option_id = DATA.get('option_id', 0)
                    item_id = DATA.get('item_id', 0)
                    count = int(DATA.get('count', 0))

                    for slug in ['attrs', 'extra_products']:
                        value = DATA.get(slug)
                        if value is not None:
                            kwargs[slug] = value

                    prices = DATA.get('prices', {})
                    if prices.get('with_wrapping') is not None:
                        kwargs['with_wrapping'] = bool(prices['with_wrapping'])
                    # for slug in ['option', 'extra', 'wrapping']:
                    #     value = prices.get(slug)
                    #     if value is not None:
                    #         kwargs['{}_price'.format(slug)] = int(value)
                    if prices.get('discount') is not None:
                        kwargs['discount'] = prices['discount']

                except ValueError:
                    data = {'result': 'error', 'error': __('Неправильный формат запроса')}
                    return JsonResponse(data, status=400)

                attrs = kwargs.get('attrs', {})
                extra_products = kwargs.get('extra_products', {})
                hash = make_hash_from_cartitem(attrs, extra_products)

                item = cart.set(product_id, hash, option_id, item_id, count, **kwargs)
                count = cart.count()
                summary = cart.summary()

                data = {'result': 'ok', 'count': count, 'summary': summary}
                if item:
                    data['item_count'] = item.count
                    data['item_price'] = to_price(item.price_int)
                    data['item_price_without_discount'] = to_price(item.total_price_without_discount)
                    data['product_link'] = item.product.get_absolute_url()

        return JsonResponse(data)
