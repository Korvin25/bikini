# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db.utils import IntegrityError
from django.http import Http404, JsonResponse
from django.views.generic import View, TemplateView
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __

from apps.catalog.models import AttributeOption, Product, ProductOption
from apps.core.mixins import JSONViewMixin
from apps.hash_utils import make_hash_from_cartitem
from apps.lk.models import WishListItem
from .utils import get_wishlist_from_request, get_wishlist_item_prices


translated_strings = (_('Неправильный формат запроса'), _('Неправильный id товара'),)


class WishListView(TemplateView):
    template_names = {
        'default': 'wishlist/wishlist.html',
        'ajax': 'wishlist/include/wishlist.html',
    }

    def get_template_names(self, *args, **kwargs):
        return (self.template_names['ajax'] if self.request.is_ajax()
                else self.template_names['default'])

    def get(self, request, *args, **kwargs):
        response = super(WishListView, self).get(request, *args, **kwargs)
        if request.is_ajax():
            html = response.rendered_content
            response = JsonResponse({'result': 'ok', 'html': html})
            response['Cache-Control'] = 'no-cache, no-store'
        return response

    def get_wishlist(self):
        profile = self.request.user
        wishlist = get_wishlist_from_request(self.request)
        products = {}
        product_options = {}
        options = {}

        # wishlist = self.get_default()

        if len(wishlist):
            product_ids = [item['product_id'] for item in wishlist]
            product_options_ids = [item['option_id'] for item in wishlist]
            options_ids = [item['attrs'].values() for item in wishlist]
            options_ids = set([el for lst in options_ids for el in lst])

            products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}
            product_options = {o.id: o for o in ProductOption.objects.filter(id__in=product_options_ids)}
            options = {o.id: o for o in AttributeOption.objects.select_related('attribute').filter(id__in=options_ids)}
            wishlist = [item for item in wishlist
                        if item['product_id'] in products.keys()
                        and item.get('option_id') in product_options.keys()]

        self.wishlist = wishlist
        self.products = products
        self.product_options = product_options
        self.options = options

    def get_context_data(self, **kwargs):
        self.get_wishlist()
        context = {
            'wishlist': self.wishlist,
            'products': self.products,
            'product_options': self.product_options,
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
                'option_id': option.id,
                'attrs': {k: v[0] for k, v in option.attrs.items()},
                'extra_products': {},
                'price': float(option.price),
            }
            item['hash'] = make_hash_from_cartitem(item['attrs'], item['extra_products'])
            wishlist.append(item)
        self.request.session['wishlist'] = wishlist
        return wishlist


class WishListAddView(JSONViewMixin, View):

    def post(self, request, *args, **kwargs):
        DATA = self.DATA
        profile = request.user

        try:
            product_id = int(DATA['product_id'])
            option_id = int(DATA['option_id'])
            attrs = DATA.get('attrs', {})
            extra_products = DATA.get('extra_products', {})
        except ValueError:
            data = {'result': 'error', 'error': __('Неправильный формат запроса')}
            return JsonResponse(data, status=400)

        hash = make_hash_from_cartitem(attrs, extra_products)
        wishlist = get_wishlist_from_request(self.request)
        # product_ids = [item['product_id'] for item in wishlist]
        # product_options_ids = [item['option_id'] for item in wishlist]

        # print hash

        if profile.is_anonymous():
            the_item = None

            for item in wishlist:
                # if item['product_id'] == product_id:
                if item['product_id'] == product_id and item['hash'] == hash:
                    the_item = item

            if the_item is None:
                the_item = {}
                wishlist.append(the_item)

            prices = get_wishlist_item_prices(product_id, option_id, extra_products)
            price_rub = prices['rub']
            price_eur = prices['eur']
            price_usd = prices['usd']

            the_item.update({
                'product_id': product_id,
                'option_id': option_id,
                'price_rub': float(price_rub),
                'price_eur': float(price_eur),
                'price_usd': float(price_usd),
                'attrs': attrs,
                'extra_products': extra_products,
                'hash': hash,
            })
            request.session['wishlist'] = wishlist

        else:
            try:
                kwargs = {'profile_id': profile.id, 'product_id': product_id, 'hash': hash}
                the_item = WishListItem.objects.filter(**kwargs).first()
                if not the_item:
                    the_item = WishListItem(option_id=option_id, **kwargs)
                the_item.option_id = option_id
                the_item.attrs = attrs
                the_item.extra_products = extra_products
                the_item.save()
            except IntegrityError:
                data = {'result': 'error', 'error': __('Неправильный id товара')}
                return JsonResponse(data, status=400)

        wishlist = get_wishlist_from_request(self.request)
        data = {'result': 'ok', 'wishlist_count': len(wishlist)}
        return JsonResponse(data)


class WishListRemoveView(JSONViewMixin, View):

    def post(self, request, *args, **kwargs):
        DATA = self.DATA
        profile = request.user

        try:
            product_id = int(DATA['product_id'])
            attrs = DATA.get('attrs', {})
            extra_products = DATA.get('extra_products', {})
        except ValueError:
            data = {'result': 'error', 'error': __('Неправильный формат запроса')}
            return JsonResponse(data, status=400)

        hash = make_hash_from_cartitem(attrs, extra_products)
        wishlist = get_wishlist_from_request(self.request)
        product_ids = [item['product_id'] for item in wishlist]

        if product_id in product_ids:
            if profile.is_anonymous():
                for i, item in enumerate(wishlist):
                    if item['product_id'] == product_id and item['hash'] == hash:
                        wishlist.pop(i)
                        break
                request.session['wishlist'] = wishlist

            else:
                try:
                    the_item = WishListItem.objects.filter(profile_id=profile.id, product_id=product_id, hash=hash).first()
                    if the_item:
                        the_item.delete()
                except IntegrityError:
                    data = {'result': 'error', 'error': __('Неправильный id товара')}
                    return JsonResponse(data, status=400)

        wishlist = get_wishlist_from_request(self.request)
        data = {'result': 'ok', 'wishlist_count': len(wishlist)}
        return JsonResponse(data)
