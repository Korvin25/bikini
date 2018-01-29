# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db.utils import IntegrityError
from django.http import Http404, JsonResponse
from django.views.generic import View, TemplateView
from django.utils import timezone

from apps.catalog.models import AttributeOption, Product
from apps.core.mixins import JSONViewMixin
from apps.lk.models import WishListItem
from .utils import get_wishlist_from_request


class WishListView(TemplateView):
    template_name = 'wishlist.html'

    def get_wishlist(self):
        profile = self.request.user
        wishlist = get_wishlist_from_request(self.request)
        products = {}
        options = {}

        # wishlist = self.get_default()

        if len(wishlist):
            product_ids = [item['product_id'] for item in wishlist]
            options_ids = [item['attrs'].values() for item in wishlist]
            options_ids = set([el for lst in options_ids for el in lst])

            products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
            options = {o.id: o for o in AttributeOption.objects.select_related('attribute').filter(id__in=options_ids)}
            wishlist = [item for item in wishlist if item['product_id'] in products.keys()]

        self.wishlist = wishlist
        self.products = products
        self.options = options

    def get_context_data(self, **kwargs):
        self.get_wishlist()
        context = {
            'wishlist': self.wishlist,
            'products': self.products,
            'options': self.options,
        }
        context.update(super(WishListView, self).get_context_data(**kwargs))
        return context

    def get_default(self):
        wishlist = []
        for p in Product.objects.all().prefetch_related('options'):
            option = p.options.first()
            item = {
                'product_id': p.id,
                'attrs': {k: v[0] for k, v in option.attrs.items()},
                'price': float(option.price),
            }
            wishlist.append(item)
        self.request.session['wishlist'] = wishlist
        return wishlist


class WishListAddView(JSONViewMixin, View):

    def post(self, request, *args, **kwargs):
        DATA = self.DATA
        profile = request.user

        try:
            product_id = int(DATA['product_id'])
            price = float(DATA.get('price', 0.0))
            attrs = DATA.get('attrs', {})
        except ValueError:
            data = {'result': 'error', 'error': 'Неправильный формат запроса'}
            return JsonResponse(data, status=400)

        wishlist = get_wishlist_from_request(self.request)
        product_ids = [item['product_id'] for item in wishlist]

        if profile.is_anonymous():
            the_item = None

            for item in wishlist:
                if item['product_id'] == product_id:
                    the_item = item

            if the_item is None:
                the_item = {}
                wishlist.append(the_item)

            the_item.update({
                'product_id': product_id,
                'price': price,
                'attrs': attrs
            })
            request.session['wishlist'] = wishlist

        else:
            try:
                the_item, _created = WishListItem.objects.get_or_create(profile_id=profile.id, product_id=product_id)
                the_item.price = price
                the_item.attrs = attrs
                the_item.save()
            except IntegrityError:
                data = {'result': 'error', 'error': 'Неправильный id товара'}
                return JsonResponse(data, status=400)

        wishlist = get_wishlist_from_request(self.request)
        print wishlist
        data = {'result': 'ok', 'wishlist_count': len(wishlist)}
        return JsonResponse(data)


class WishListRemoveView(JSONViewMixin, View):

    def post(self, request, *args, **kwargs):
        DATA = self.DATA
        profile = request.user

        try:
            product_id = int(DATA['product_id'])
        except ValueError:
            data = {'result': 'error', 'error': 'Неправильный формат запроса'}
            return JsonResponse(data, status=400)

        wishlist = get_wishlist_from_request(self.request)
        product_ids = [item['product_id'] for item in wishlist]

        if product_id in product_ids:
            if profile.is_anonymous():
                for i, item in enumerate(wishlist):
                    if item['product_id'] == product_id:
                        wishlist.pop(i)
                        break
                request.session['wishlist'] = wishlist

            else:
                try:
                    the_item = WishListItem.objects.get(profile_id=profile.id, product_id=product_id)
                    the_item.delete()
                except WishListView.DoesNotExist:
                    pass
                except IntegrityError:
                    data = {'result': 'error', 'error': 'Неправильный id товара'}
                    return JsonResponse(data, status=400)

        wishlist = get_wishlist_from_request(self.request)
        print wishlist
        data = {'result': 'ok', 'wishlist_count': len(wishlist)}
        return JsonResponse(data)
