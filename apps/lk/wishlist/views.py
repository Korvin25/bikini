# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import Http404, JsonResponse
from django.views.generic import View, TemplateView
from django.utils import timezone

from apps.catalog.models import AttributeOption, Product
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


class WishListAddView(View):
    pass


class WishListRemoveView(View):
    pass
