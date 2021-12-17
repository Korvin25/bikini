# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import uuid

from django.conf import settings
# from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from django.views.generic import View, UpdateView

from apps.analytics.conf import SESSION_YM_CLIENT_ID_KEY
from apps.analytics.utils import update_traffic_source
from apps.cart.cart import Cart
from apps.cart.forms import CartCheckoutForm
from apps.cart.models import Cart as CartModel
from apps.cart.utils import update_cart_with_payment
from apps.core.mixins import JSONFormMixin
from apps.core.templatetags.core_tags import to_price
from apps.currency.utils import get_currency
from apps.hash_utils import make_hash_from_cartitem
from apps.third_party.yookassa import Configuration, Payment
from apps.third_party.yookassa.domain.notification import WebhookNotification
from apps.utils import absolute, get_error_message


translated_strings = (_('Корзина пуста'), _('Неправильный формат запроса'), _('Неправильный id товара'),
                      _('Выберите способы оставки и оплаты'), _('Выберите способ доставки'), _('Выберите способ оплаты'))

Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

l_yookassa = logging.getLogger('yookassa')


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

        # basket = self.cart.cart

        # delivery_method = basket.delivery_method
        # payment_method = basket.payment_method
        delivery_method = kw.get('delivery_method_id')
        payment_method = kw.get('payment_method_id')

        if not (delivery_method or payment_method):
            data = {'result': 'error', 'error': __('Выберите способы доставки и оплаты')}
            status = 400
        elif not delivery_method:
            data = {'result': 'error', 'error': __('Выберите способ доставки')}
            status = 400
        elif not payment_method:
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
        'postal_code': 'postal_code',
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

            # -- сбрасываем CART_ID --
            if self.request.session.get('CART_ID'):
                del self.request.session['CART_ID']

            # -- проставляем поля --
            for k in self.mapping.keys():
                key = {'country': 'country_id'}.get(k, k)
                if not getattr(profile, key, None) or key in ['delivery_method_id', 'payment_method_id']:
                    setattr(profile, key, getattr(cart, key))
                if not profile.has_email and form.cleaned_data.get('email'):
                    profile.email = form.cleaned_data['email']
                    profile.has_email = True
            profile.orders_num = profile.orders_num + 1
            profile.save()

            # -- аналитика --
            cart.ym_client_id = self.request.session.get(SESSION_YM_CLIENT_ID_KEY)
            if not cart.ym_client_id:
                for key in ['ym_client_id', 'ym_source', 'ym_source_detailed']:
                    setattr(cart, key, getattr(profile, key, None))
            cart.save()
            if cart.ym_client_id and not cart.ym_source:
                update_traffic_source(cart)

            # -- убираем скидки из профиля --
            profile.discount_code = ''
            profile.discount_used = False
            profile.save()

            # -- начинаем собирать ответ на фронт --
            data = {
                'count': cart.count(),
                'summary': cart.show_summary(),
                'ya_summary': cart.summary_c,
                'ya_currency': cart.get_yandex_currency(),
                'order_number': cart.number,
            }

            # -- главная развилка по типу оплаты --
            payment_type = cart.payment_type
            if payment_type == 'yookassa':
                # 1/3: yookassa
                try:
                    # создаем платеж
                    _return_url = reverse('cart_api:yookassa', kwargs={'pk': cart.id})
                    payment = Payment.create({
                        "amount": {
                            "value": unicode(cart.summary_rub),  # noqa
                            "currency": 'RUB',
                        },
                        "confirmation": {
                            "type": "redirect",
                            "return_url": absolute(_return_url),
                        },
                        "capture": True,
                        "description": '{} {}'.format(__('Заказ №'), cart.number),
                    }, uuid.uuid4())

                    # обновляем поля, связанные с yookassa
                    redirect_url = payment.confirmation.confirmation_url
                    cart.yoo_redirect_url = redirect_url
                    for key in ['id', 'status', 'paid', 'test']:
                        setattr(cart, 'yoo_{}'.format(key), getattr(payment, key))
                    cart.save()

                    # обновляем ответ на фронт
                    data.update({
                        'result': 'redirect',
                        'redirect_url': redirect_url,
                    })

                except Exception as exc:
                    try:
                        err_message = get_error_message(exc)
                    except Exception:
                        err_message = 'Неизвестная ошибка'
                    cart.yoo_paid = False
                    cart.yoo_status = 'error'
                    cart.save()
                    data = {'result': 'error', 'error': err_message}
                    return JsonResponse(data, status=400)

            # elif payment_type == 'paypal':
            #     # 2/3: paypal # TODO

            else:
                # 3/3: наличные
                # -- отправка имейлов --
                cart.send_order_emails()

                # -- остатки на складе --
                cart.update_in_stock()

                # -- спец.предложения --
                specials = cart.get_specials()
                has_specials = bool(specials)
                if has_specials:
                    data['specials_html'] = cart.get_specials_html(specials=specials, request=self.request)
                popup = '#step5' if has_specials else '#step4'

                data.update({
                    'result': 'ok',
                    'popup': popup,
                })
            return JsonResponse(data)

        else:
            data = {'result': 'error', 'error': __('Корзина пуста'), 'error_code': 'CART_EMPTY'}
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


class YooKassaWebhookView(View):
    """
    Обрабатываем webhook-запрос от ЮКассы
    """

    def post(self, request, *args, **kwargs):
        event_json = json.loads(request.body)
        notification_object = WebhookNotification(event_json)
        payment = notification_object.object
        l_yookassa.info('----')
        l_yookassa.info('NEW event: payment {}; status {}'.format(payment.id, payment.status))

        # обновляем cart в базе
        cart = CartModel.objects.get(yoo_id=payment.id)
        l_yookassa.info('cart id: {}; cart status {}'.format(cart.id, cart.yoo_status))
        update_cart_with_payment(cart, payment, logger=l_yookassa)
        return HttpResponse(status=200)


class YooKassaCartView(View):
    """
    Обрабатываем человека, вернувшегося на redirect_url из ЮКассы
    """

    def get(self, request, *args, **kwargs):
        # получаем объект cart
        cart = get_object_or_404(CartModel, id=kwargs.get('pk'))

        # запрашиваем данные о платеже (и обновляем его в случае необходимости)
        _id = str(cart.yoo_id)
        payment = Payment.find_one(_id)
        l_yookassa.info('----')
        l_yookassa.info('NEW visit: payment {}; status {}'.format(payment.id, payment.status))
        l_yookassa.info('cart id: {}; cart status {}'.format(cart.id, cart.yoo_status))
        update_cart_with_payment(cart, payment, logger=l_yookassa)

        # определяем человека
        profile = cart.profile
        if request.user != profile:
            return HttpResponseRedirect(reverse('home'))
            # profile.backend = 'django.contrib.auth.backends.ModelBackend'
            # login(request, profile)

        # собираем redirect_url
        redirect_url = '{}?tab=orders&order_id={}'.format(reverse('profile'), cart.id)
        return HttpResponseRedirect(redirect_url)
