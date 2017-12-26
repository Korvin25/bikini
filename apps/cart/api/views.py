# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import Http404, JsonResponse
from django.views.generic import View

from apps.catalog.models import Product
from apps.cart.cart import Cart


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

        else:
            try:
                DATA = json.loads(request.body)
            except ValueError:
                data = {'result': 'error', 'error': 'Неправильный формат запроса'}
                return JsonResponse(data, status=400)

            if self.action == 'remove':
                cart.remove(item_id=DATA.get('item_id', 0))
                data = {'result': 'ok'}

            elif self.action == 'set':
                try:
                    product_id = DATA.get('product_id', 0)
                    option_id = DATA.get('option_id', 0)
                    count = int(DATA.get('count', 0))

                    attrs = DATA.get('attrs', {})
                    extra_products = DATA.get('extra_products', {})
                    prices = DATA.get('prices', {})

                    option_price = int(prices.get('option', 0))
                    extra_price = int(prices.get('extra', 0))
                    wrapping_price = int(prices.get('wrapping', 0))
                except ValueError:
                    data = {'result': 'error', 'error': 'Неправильный формат запроса'}
                    return JsonResponse(data, status=400)

                kwargs = {
                    'attrs': attrs,
                    'extra_products': extra_products,
                    'option_price': option_price,
                    'extra_price': extra_price,
                    'wrapping_price': wrapping_price,
                }
                cart.set(product_id, option_id, count, **kwargs)

                count = cart.count()
                summary = cart.summary()
                data = {'result': 'ok', 'count': count, 'summary': summary}

        return JsonResponse(data)


        # else:
        #     product = Product.objects.filter(id=int(request.POST.get('product_id'))).first()
        #     try:
        #         quantity = int(request.POST.get('quantity', 1))

        #     except ValueError:
        #         error = 'Введите целое положительное число'

        #     else:
        #         if product:
        #             if self.action == 'set':
        #                 cart.set(product, quantity)

        #             elif self.action == 'add':
        #                 cart.add(product, quantity)

        #             elif self.action == 'remove':
        #                 cart.remove(product)

        #         else:
        #             error = 'Неправильный номер товара'

        # if error:
        #     data = {'result': 'error', 'error': error}
        # else:
        #     data = cart.get_basket()
        # return JsonResponse(data)
