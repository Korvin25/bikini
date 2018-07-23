# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import InvalidOperation

from django.contrib import messages
from django.db.models import F
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from pytils.numeral import choose_plural

from ..catalog.models import Product, ProductOption, ProductExtraOption
from ..core.mixins import JSONViewMixin


class IncreaseInStockView(JSONViewMixin, View):

    def post(self, request, *args, **kwargs):
        status = 200
        data = {'result': 'ok', 'next': '/admin/catalog/product/'}

        # проверяем товары
        try:
            product_ids = [int(p_id) for p_id in self.DATA.get('products', '').split(',')]
            products = Product.objects.filter(id__in=product_ids)
        except ValueError:
            status = 400
            data = {'result': 'error', 'error_message': 'Неправильные ID товаров.'}
            return JsonResponse(data, status=status)

        count = products.count()
        if not count:
            status = 400
            data = {'result': 'error', 'error_message': 'Неправильные ID товаров.'}
            return JsonResponse(data, status=status)

        # проверяем число
        try:
            increase_to = int(float(self.DATA.get('increase_to')))
            if increase_to == 0:
                raise ValueError
        except ValueError:
            status = 400
            data = {'result': 'error', 'error_message': 'Введите целое ненулевое число.'}
            return JsonResponse(data, status=status)

        # увеличиваем/уменьшаем
        ProductOption.objects.filter(product_id__in=products).update(in_stock=F('in_stock')+increase_to)
        ProductExtraOption.objects.filter(product_id__in=products).update(in_stock=F('in_stock')+increase_to)

        # везде выравниваем в ноль сразу же
        ProductOption.objects.filter(in_stock__lt=0).update(in_stock=0)
        ProductExtraOption.objects.filter(in_stock__lt=0).update(in_stock=0)

        # пилим message и редиректим домой
        count_label = choose_plural(count, ('товара', 'товаров', 'товаров'))
        messages.success(request, 'Количество на складе у {} {} успешно обновлено.'.format(count, count_label))
        return JsonResponse(data, status=status)


class ChangeProductView(JSONViewMixin, View):

    def post(self, request, *args, **kwargs):
        status = 200
        data = {'result': 'ok', 'success_message': 'Данные о товаре успешно обновлены.'}

        # проверяем товары
        try:
            product = Product.objects.get(id=self.DATA.get('product'))
        except (ValueError, Product.DoesNotExist) as exc:
            print exc
            status = 400
            data = {'result': 'error', 'error_message': 'Неправильный ID товара.'}
            return JsonResponse(data, status=status)

        for k, v in self.DATA.iteritems():
            if v is not None:

                if k.startswith('product_'):
                    key = k.split('product_')[1]
                    try:
                        setattr(product, key, v)
                        product.save()
                    except (ValueError, InvalidOperation) as exc:
                        print exc
                        pass

                elif k.startswith('option_'):
                    key = ('vendor_code' if k.startswith('option_vendor_code_')
                         else 'in_stock' if k.startswith('option_in_stock_')
                         else 'price_rub' if k.startswith('option_price_rub_')
                         else 'price_eur' if k.startswith('option_price_eur_')
                         else 'price_usd' if k.startswith('option_price_usd_')
                         else None)
                    if key:
                        try:
                            _id = k.split('option_{}_'.format(key))[1]
                            option = product.options.get(id=_id)
                            if key == 'in_stock':
                                v = int(float(v))
                                v = 0 if v < 0 else v
                            setattr(option, key, v)
                            option.save()
                        except (ProductOption.DoesNotExist, ValueError, InvalidOperation) as exc:
                            print exc
                            pass

                elif k.startswith('extra_p_'):
                    key = ('vendor_code' if k.startswith('extra_p_vendor_code_')
                         else 'in_stock' if k.startswith('extra_p_in_stock_')
                         else 'price_rub' if k.startswith('extra_p_price_rub_')
                         else 'price_eur' if k.startswith('extra_p_price_eur_')
                         else 'price_usd' if k.startswith('extra_p_price_usd_')
                         else None)
                    if key:
                        try:
                            _id = k.split('extra_p_{}_'.format(key))[1]
                            extra_p = product.extra_options.get(id=_id)
                            if key == 'in_stock':
                                v = int(float(v))
                                v = 0 if v < 0 else v
                            setattr(extra_p, key, v)
                            extra_p.save()
                        except (ProductExtraOption.DoesNotExist, ValueError, InvalidOperation) as exc:
                            print exc
                            pass

        return JsonResponse(data, status=status)
