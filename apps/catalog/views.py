# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db.models import Q, Max, Min
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from .models import Attribute, Category, GiftWrapping, Product, ProductOption
from ..core.templatetags.core_tags import to_int_plus


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
        if self.request.is_ajax():
            return self.TEMPLATES['ajax'] if self.map is False else self.TEMPLATES['map_ajax']
        return self.TEMPLATES['default']

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
        self.category = (None if self.with_category is False
                         else _get_category_from_kwargs(request=self.request, sex=self.sex, slug=self.kwargs.get('slug')))
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

        qs = Product.objects.select_related('category').prefetch_related('options').filter(show=True)
        if self.category:
            qs = qs.filter(category_id=self.category.id)
        else:
            qs = qs.filter(category__sex=self.sex)

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
        qs = qs.order_by('-id')

        self.qs = qs
        return qs

    def get_context_data(self, **kwargs):
        category = self.get_category()
        products = self.get_queryset()
        context = {
            'category': category,
            'sex': self.sex,
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

    def get_product(self):
        self.category = _get_category_from_kwargs(request=self.request, sex=self.sex, slug=self.kwargs.get('category_slug'))
        self.product = _get_product_from_kwargs(request=self.request, category=self.category,
                                                slug=self.kwargs.get('slug'), pk=self.kwargs.get('pk'))
        return self.product

    def get_attributes(self):
        _attrs = self.product.attributes.select_related('neighbor').prefetch_related('options').filter(display_type__gte=1)

        def _get_attr_dict(attr, with_neighbor=False):
            _attr = {}
            options_ids = self.product.attrs.get(attr.slug, list())
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
                if with_neighbor and attr.neighbor_id:
                    _neighbor = _get_attr_dict(attr.neighbor, with_neighbor=False)
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

    def get_attrs_json(self):
        attrs_data = {
            'attrs': {},
            'options': {},
            'option': {},
        }

        for type, attr_list in self.attrs.iteritems():
            for attr in attr_list:
                attrs_data['attrs'][attr['slug']] = type

        for i, option in enumerate(self.product.options.all()):
            option_dict = {
                'id': option.id,
                'attrs': option.attrs,
                'price': to_int_plus(option.price_rub or self.product.price_rub or 0),
                'in_stock': option.in_stock,
            }
            attrs_data['options'][option.id] = option_dict
            if i == 0:
                attrs_data['option'] = option_dict

        print attrs_data
        attrs_json = json.dumps(attrs_data)
        return attrs_json

    def get_context_data(self, **kwargs):
        product = self.get_product()
        category = self.category
        self.get_attributes()
        context = {
            'product': product,
            'category': category,
            'sex': self.sex,
            'attrs': self.attrs,
            'attrs_dict': self.attrs_dict,
            'attrs_ids': self.attrs_ids,
            'photos': product.photos.all(),
            'gift_wrapping_price': GiftWrapping.get_price(),
            'attrs_json': self.get_attrs_json(),
        }
        context.update(super(ProductView, self).get_context_data(**kwargs))
        return context


def _get_category_from_kwargs(request, sex, slug):
    category = None
    try:
        category = get_object_or_404(Category, sex=sex, slug=slug)
    except Http404 as exc:
        if request.LANGUAGE_CODE != 'ru':
            try:
                category = get_object_or_404(Category, sex=sex, slug_en=slug)
            except Http404:
                category = get_object_or_404(Category, sex=sex, slug_ru=slug)
        else:
            raise exc
    return category


def _get_product_from_kwargs(request, category, slug, pk):
    product = None
    try:
        product = get_object_or_404(Product, category_id=category.id, slug=slug, pk=pk, show=True)
    except Http404 as exc:
        if request.LANGUAGE_CODE != 'ru':
            try:
                product = get_object_or_404(Product, category_id=category.id, slug_en=slug, pk=pk, show=True)
            except Http404:
                product = get_object_or_404(Product, category_id=category.id, slug_ru=slug, pk=pk, show=True)
        else:
            raise exc
    return product
