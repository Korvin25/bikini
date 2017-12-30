# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import Http404, JsonResponse
from django.views.generic import View, UpdateView
from django.utils import timezone

from apps.catalog.models import Product
from apps.cart.cart import Cart
from apps.cart.forms import CartCheckoutForm
from apps.core.mixins import JSONFormMixin


class EmptyCartError(Exception):
    pass


class CheckCartMixin(object):

    def check_cart(self, cart):
        cart_items = cart.cart.cartitem_set.all()
        for item in cart_items:
            if item.count == 0:
                item.delete()
        cart_items = cart.cart.cartitem_set.all().select_related('product')
        if not cart_items:
            raise EmptyCartError


class CartStepBaseView(CheckCartMixin, View):

    def dispatch(self, request, *args, **kwargs):
        self.cart = Cart(request)
        self.DATA = {}

        try:
            self.check_cart(self.cart)
        except EmptyCartError:
            data = {'result': 'error', 'error': 'Корзина пуста', 'error_code': 'CART_EMPTY'}
            return JsonResponse(data, status=400)

        try:
            self.DATA = json.loads(request.body)
        except ValueError:
            data = {'result': 'error', 'error': 'Неправильный формат запроса'}
            return JsonResponse(data, status=400)

        return super(CartStepBaseView, self).dispatch(request, *args, **kwargs)


class Step0View(CartStepBaseView):
    """
    Проверяем на залогиненность
    """

    def post(self, request, *args, **kwargs):
        if 'additional_info' in self.DATA:
            kwargs = {'additional_info': self.DATA['additional_info']}
            self.cart.update(**kwargs)

        if request.user.is_anonymous():
            data = {'result': 'ok', 'popup': '#step1'}
        else:
            data = {'result': 'ok', 'popup': '#step3'}
        return JsonResponse(data)


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
    }

    def dispatch(self, request, *args, **kwargs):
        self.cart = Cart(request)

        try:
            self.check_cart(self.cart)
        except EmptyCartError:
            data = {'result': 'error', 'error': 'Корзина пуста', 'error_code': 'CART_EMPTY'}
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
            cart.summary = cart.get_summary()
            cart.save()
            super(Step3View, self).form_valid(form)

            profile = cart.profile

            # send_customer_order_email(order.profile, order=cart)
            # send_admin_order_email(order=cart)

            if self.request.session.get('CART_ID'):
                del self.request.session['CART_ID']

            for k in self.mapping.keys():
                key = {'country': 'country_id'}.get(k)
                if not getattr(profile, key):
                    setattr(profile, key, getattr(cart, key))
            profile.save()

            count = cart.count()
            summary = cart.show_summary()
            order_number = cart.number

            data = {'result': 'ok', 'popup': '#step4', 'count': count, 'summary': summary, 'order_number': order_number}
            return JsonResponse(data)

        else:
            data = {'result': 'error', 'error_message': 'Корзина пуста'}
            return JsonResponse(data, status=400)


class Step4View(CartStepBaseView):

    def post(self, request, *args, **kwargs):
        data = {'result': 'ok'}
        return JsonResponse(data)


class UpdateCartView(View):

    def post(self, request, *args, **kwargs):
        data = {}
        DATA = {}
        cart = Cart(request)

        try:
            DATA = json.loads(request.body)
        except ValueError:
            data = {'result': 'error', 'error': 'Неправильный формат запроса'}
            return JsonResponse(data, status=400)

        cart.update(**DATA)
        data = {'result': 'ok'}
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
                data = {'result': 'error', 'error': 'Неправильный формат запроса'}
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
                    for slug in ['option', 'extra', 'wrapping']:
                        value = prices.get(slug)
                        if value is not None:
                            kwargs['{}_price'.format(slug)] = int(value)

                except ValueError:
                    data = {'result': 'error', 'error': 'Неправильный формат запроса'}
                    return JsonResponse(data, status=400)

                item = cart.set(product_id, option_id, item_id, count, **kwargs)
                count = cart.count()
                summary = cart.summary()

                data = {'result': 'ok', 'count': count, 'summary': summary}
                if item:
                    data['item_count'] = item.count
                    data['item_price'] = item.price_int

        return JsonResponse(data)
