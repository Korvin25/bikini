# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
import json

from django.db.models import Q, Max, Min
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from ..core.templatetags.core_tags import to_int_plus
from ..core.http_utils import get_object_from_slug_and_kwargs
from ..lk.wishlist.utils import get_wishlist_from_request
from .models import Attribute, Category, GiftWrapping, Product, ProductOption, SpecialOffer


class ProductsView(TemplateView):
    with_category = False
    sex = 'female'
    TEMPLATES = {
        'default': 'catalog/products.html',
        'men': 'catalog/products_men.html',
        'women': 'catalog/products_women.html',
        'ajax': 'catalog/include/products.html',
    }

    def get_template_names(self):
        TEMPLATES = self.TEMPLATES
        is_ajax = self.request.is_ajax()
        with_category = self.with_category
        return {
            is_ajax: TEMPLATES['ajax'],
            (not is_ajax and with_category): TEMPLATES['default'],
            (not is_ajax and not with_category and self.sex == 'female'): TEMPLATES['women'],
            (not is_ajax and not with_category and self.sex == 'male'): TEMPLATES['men'],
        }.get(True)

    def get_category(self):
        kw = {'sex': self.sex}
        self.category = (None if self.with_category is False
                         else get_object_from_slug_and_kwargs(self.request, model=Category, slug=self.kwargs.get('slug'), **kw))
        return self.category

    def get_attributes(self):
        all_attrs_values = ProductOption.objects.select_related('product').filter(product__in=self.base_qs).values_list('attrs', flat=True)

        a_keys = set()
        a_values = list()
        for attrs in all_attrs_values:
            for k, v in attrs.items():
                a_keys.add(k)
                a_values.extend(v)
        a_values = set(a_values)

        if self.category:
            attrs = self.category.attributes.prefetch_related('options').filter(display_type__gte=2)
        else:
            attrs = Attribute.objects.prefetch_related('options', 'categories').filter(display_type__gte=3,
                                                                                       categories__sex=self.sex).distinct()

        attrs_dict = {'color': [], 'size': [], 'style': [], 'text': []}
        for attr in attrs:
            if attr.slug in a_keys:
                attrs_dict[attr.attr_type].append(attr)

        self.attrs = attrs_dict
        self.a_keys = a_keys
        self.a_values = a_values
        return self.attrs

    def get_attrs_filter(self):

        def _get_attrs_queries(query):
            queries = []
            for k, v in query.iteritems():
                _lookups = []
                for value in v:
                    q = 'Q(attrs__{}__contains={})'.format(k, value)
                    _lookups.append(eval(q))
                _query = _lookups[0]
                for q in _lookups[1:]:
                    _query |= q
                queries.append(_query)
            return queries

        queries = _get_attrs_queries(self.f.get('attrs', dict()))
        self.attrs_filter = queries
        return queries

    def get_filter(self):
        f = {}
        if self.f.get('price_from'):
            f['price_rub__gte'] = self.f['price_from']
        if self.f.get('price_to'):
            f['price_rub__lte'] = self.f['price_to']
        self.filter = f
        return f

    def get_queryset(self, **kwargs):
        GET = self.request.GET
        self.f = {'attrs': {}, 'attrs_values': []}

        qs = Product.objects.prefetch_related('categories', 'options').filter(show=True)
        if self.category:
            qs = qs.filter(categories=self.category.id)
        else:
            qs = qs.filter(categories__sex=self.sex)

        self.base_qs = qs
        self.price_min_max = qs.aggregate(Min('price_rub'), Max('price_rub'))
        self.get_attributes()

        price_from = GET.get('price_from')
        price_to = GET.get('price_to')
        if price_from:
            try:
                self.f['price_from'] = int(price_from)
            except ValueError:
                pass
        if price_to:
            try:
                self.f['price_to'] = int(price_to)
            except ValueError:
                pass

        for k in GET.keys():
            if k.startswith('_') and k != '_':
                key = k[1:]
                if key in self.a_keys:
                    _values = GET.getlist(k)
                    values = []
                    for v in _values:
                        try:
                            option_id = int(v)
                            if option_id in self.a_values:
                                values.append(option_id)
                                self.f['attrs_values'].append(option_id)
                        except ValueError:
                            pass
                    if values:
                        self.f['attrs'][key] = values

        qs = qs.filter(*self.get_attrs_filter())
        qs = qs.filter(**self.get_filter()).distinct()
        if self.category:
            qs = qs.order_by('order', '-id')
            qs = list(qs)
        else:
            qs = qs.order_by('categories', 'order', '-id')
            # убираем дубликаты (ибо distinct после сортировки по m2m-полю почему-то не срабатывает)
            qs = list(OrderedDict((el, None) for el in qs))
        self.qs = qs
        return qs

    def get_context_data(self, **kwargs):
        category = self.get_category()
        products = self.get_queryset()
        context = {
            'category': category,
            'sex': self.sex,
            'category_or_sex': category or self.sex,
            'categories': Category.objects.filter(sex=self.sex),
            'products': products,
            'attrs': self.attrs,
            'attrs_options': self.a_values,
            'price_min_max': self.price_min_max,
            'f': self.f,
            'filter': self.filter,
        }
        context.update(super(ProductsView, self).get_context_data(**kwargs))
        return context


class ProductView(TemplateView):
    template_name = 'catalog/product.html'
    sex = 'female'
    discount = 0

    def get_product(self):
        kw = {'sex': self.sex}
        self.category = get_object_from_slug_and_kwargs(self.request, model=Category, slug=self.kwargs.get('category_slug'), **kw)

        kw = {'pk': self.kwargs.get('pk'), 'categories': self.category, 'show': True}
        self.product = get_object_from_slug_and_kwargs(self.request, model=Product, slug=self.kwargs.get('slug'), **kw)
        return self.product

    def get_attributes(self):
        _attrs = self.product.attributes.select_related('neighbor').prefetch_related('options').filter(display_type__gte=1)

        def _get_attr_dict(attr, options_source=self.product.attrs, with_neighbor=False):
            _attr = {}
            options_ids = options_source.get(attr.slug, list())
            if options_ids:
                _attr = {
                    'attr': attr,
                    'id': attr.id,
                    'title': attr.title,
                    'slug': attr.slug,
                    'attr_type': attr.attr_type,
                    'options': attr.options.filter(id__in=options_ids),
                    'options_ids': options_ids,
                }
                if with_neighbor and attr.attr_type == 'style' and attr.neighbor_id:
                    _neighbor = _get_attr_dict(attr.neighbor, options_source=options_source, with_neighbor=False)
                    if _neighbor:
                        _attr['neighbor'] = _neighbor
                        _attr['neighbor_id'] = attr.neighbor_id
            return _attr

        attrs = {'color': [], 'size': [], 'style': [], 'text': []}
        attrs_dict = {}
        attrs_ids = []
        for attr in _attrs:
            _attr = _get_attr_dict(attr, with_neighbor=True)
            if _attr:
                attrs[attr.attr_type].append(_attr)
                attrs_dict[attr.id] = _attr
                attrs_ids.append(attr.id)
        self.attrs = attrs
        self.attrs_dict = attrs_dict
        self.attrs_ids = attrs_ids

        extra_products = []
        for extra_p in self.product.extra_products.prefetch_related('extra_product__attributes__neighbor', 'extra_product__attributes__options'):
            _attrs = extra_p.extra_product.attributes.filter(display_type__gte=1)
            attrs = {'color': [], 'size': [], 'style': [], 'text': []}
            attrs_dict = {}
            attrs_ids = []

            for attr in _attrs:
                _attr = _get_attr_dict(attr, options_source=extra_p.attrs, with_neighbor=True)
                if _attr:
                    attrs[attr.attr_type].append(_attr)
                    attrs_dict[attr.id] = _attr
                    attrs_ids.append(attr.id)

            _attr = None
            if attrs['style']:
                _attr = attrs['style'][0]
                if _attr.get('neighbor'):
                    _attr = _attr['neighbor']
            elif attrs['size']:
                _attr = attrs['size'][0]
            elif attrs['color']:
                _attr = attrs['color'][0]
            _attr['price'] = to_int_plus(extra_p.price or 0)

            extra_product_dict = {
                'id': extra_p.extra_product.id,
                'title': extra_p.extra_product.title,
                'slug': extra_p.extra_product.slug,
                'price': to_int_plus(extra_p.price or 0),
                'attrs': attrs,
                'attrs_dict': attrs_dict,
                'attrs_ids': attrs_ids,
                'attrs_json': extra_p.attrs,
                'in_stock': extra_p.in_stock,
            }
            extra_products.append(extra_product_dict)
        self.extra_products = extra_products

    def get_chosen_options(self):
        chosen_options = {k[1:]: v for k, v in self.request.GET.items() if k.startswith('_') and v}
        self.chosen_options = chosen_options

    def get_wrapping_price(self):
        wrapping_price = to_int_plus(GiftWrapping.get_price() or 0)
        self.wrapping_price = wrapping_price

    def get_data_json(self):
        data = {
            'attrs': {},  # {slug: {id, slug, type, title, category}}
            'options': {},  # {id: {id, attrs: <json>, price, in_stock}}
            'option': {},  # {id, attrs: <json>, price, in_stock}
            'prices': {
                'option': to_int_plus(self.product.price_rub or 0),
                'discount': 0,
                'extra': 0,
                'wrapping': 0,
                'count': 1,
                'maximum_in_stock': 0,
                'extra_maximum_in_stock': 0,
                'total': 0,
            },
            'extra_products': {},  # {id: {id, slug, title, attrs: <json>, price, in_stock}}
            'extra_p_selected': {},
        }

        self.with_wrapping = False
        if self.chosen_options.get('with_wrapping'):
            data['prices']['wrapping'] = self.wrapping_price
            self.with_wrapping = True

        if self.chosen_options.get('count'):
            try:
                data['prices']['count'] = int(self.chosen_options['count'])
            except ValueError:
                pass

        for type, attr_list in self.attrs.iteritems():
            for attr in attr_list:
                data['attrs'][attr['slug']] = {
                    'id': attr['id'],
                    'slug': attr['slug'],
                    'type': attr['attr_type'],
                    'title': attr['title'],
                    'category': 'primary',
                }

        for i, option in enumerate(self.product.options.all()):
            option_dict = {
                'id': option.id,
                'attrs': option.attrs,
                'price': to_int_plus(option.price_rub or self.product.price_rub or 0),
                'in_stock': option.in_stock,
            }
            data['options'][option.id] = option_dict
            if i == 0 or (data['prices']['maximum_in_stock'] == 0 and option_dict['in_stock']):
                data['option'] = option_dict
                data['prices']['option'] = option_dict['price']
                data['prices']['maximum_in_stock'] = option_dict['in_stock']

        for extra_p in self.extra_products:
            extra_p_dict = {
                'id': extra_p['id'],
                'title': extra_p['title'],
                'slug': extra_p['slug'],
                'price': extra_p['price'],
                'attrs': extra_p['attrs_json'],
                'in_stock': extra_p['in_stock'],
            }
            for attr in extra_p['attrs_dict'].values():
                data['attrs'][attr['slug']] = {
                    'id': attr['id'],
                    'slug': attr['slug'],
                    'type': attr['attr_type'],
                    'title': attr['title'],
                    'category': 'extra',
                }
            data['extra_products'][extra_p['id']] = extra_p_dict

        p = data['prices']
        p['total_price'] = (p['option']+p['extra'])*p['count'] + p['wrapping'];

        self.have_option = bool(data['option'])
        self.price = data['prices']['total_price']
        self.count = data['prices']['count']
        self.maximum_in_stock = data['prices']['maximum_in_stock']

        data['prices']['discount'] = self.discount
        self.data = data
        self.data_json = json.dumps(data)

    def get_from_wishlist(self):
        wishlist = get_wishlist_from_request(self.request)
        wishlist_data = {
            'product_id': self.product.id,
            'option_id': self.data['option'].get('id'),
            'price': self.data['prices']['option'],
            'attrs': {},
        }
        wishlist_item = None
        for item in wishlist:
            if self.product.id == item['product_id']:
                wishlist_item = item
                break
        in_wishlist = bool(wishlist_item)

        if wishlist_item:
            wishlist_data['price'] = wishlist_item['price']
            wishlist_data['attrs'] = wishlist_item['attrs']

        wishlist_data['attrs_json'] = json.dumps(wishlist_data['attrs'])
        self.in_wishlist = in_wishlist
        self.wishlist_data = wishlist_data

    def get_context_data(self, **kwargs):
        product = self.get_product()
        category = self.category
        self.get_attributes()
        self.get_chosen_options()
        self.get_wrapping_price()
        self.get_data_json()
        self.get_from_wishlist()
        context = {
            'product': product,
            'category': category,
            'sex': self.sex,
            'attrs': self.attrs,
            'attrs_dict': self.attrs_dict,
            'attrs_ids': self.attrs_ids,
            'extra_products': self.extra_products,
            'photos': product.photos.all(),
            'gift_wrapping_price': self.wrapping_price,
            'have_option': self.have_option,
            'price': self.price,
            'count': self.count,
            'maximum_in_stock': self.maximum_in_stock,
            'data_json': self.data_json,
            'discount': self.discount,
            'chosen_options': self.chosen_options,
            'in_wishlist': self.in_wishlist,
            'wishlist_data': self.wishlist_data,
            'with_wrapping': self.with_wrapping,
        }
        context.update(super(ProductView, self).get_context_data(**kwargs))
        return context


class ProductWithDiscountView(ProductView):

    def get(self, request, *args, **kwargs):
        product = self.get_product()
        profile = request.user
        special_offer = SpecialOffer.get_offer()

        if (profile.is_anonymous() or not profile.can_get_discount
            or not special_offer or special_offer.product_id != product.id
            or kwargs.get('code') != profile.discount_code):
            return HttpResponseRedirect(product.get_absolute_url())

        self.discount = special_offer.discount
        return super(ProductWithDiscountView, self).get(request, *args, **kwargs)

    # def get_context_data(self, **kwargs):
    #     context = super(ProductWithDiscountView, self).get_context_data(**kwargs)
    #     data = 

    #     product = self.get_product()
    #     category = self.category
    #     self.get_attributes()
    #     self.get_data_json()
    #     context = {
    #         'product': product,
    #         'category': category,
    #         'sex': self.sex,
    #         'attrs': self.attrs,
    #         'attrs_dict': self.attrs_dict,
    #         'attrs_ids': self.attrs_ids,
    #         'extra_products': self.extra_products,
    #         'photos': product.photos.all(),
    #         'gift_wrapping_price': to_int_plus(GiftWrapping.get_price() or 0),
    #         'have_option': self.have_option,
    #         'price': self.price,
    #         'count': self.count,
    #         'maximum_in_stock': self.maximum_in_stock,
    #         'data_json': self.data_json,
    #     }
    #     context.update(super(ProductView, self).get_context_data(**kwargs))
    #     return context
