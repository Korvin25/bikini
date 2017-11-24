# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

from .models import Category, Product, Attribute


class ProductsView(TemplateView):
    with_category = False
    sex = 'female'

    def get_template_names(self):
        return {
            self.with_category: 'catalog/products.html',
            (not self.with_category and self.sex == 'female'): 'catalog/products_women.html',
            (not self.with_category and self.sex == 'male'): 'catalog/products_men.html',
        }.get(True)

    def get_category(self):
        self.category = (None if self.with_category is False
                         else _get_category_from_kwargs(request=self.request, sex=self.sex, slug=self.kwargs.get('slug')))
        return self.category

    def get_queryset(self, **kwargs):
        qs = Product.objects.select_related('category').filter(show=True)
        if self.category:
            qs = qs.filter(category_id=self.category.id)
        else:
            qs = qs.filter(category__sex=self.sex)
        qs = qs.order_by('-id')
        self.qs = qs
        return qs

    def get_attributes(self):
        if self.category:
            attrs = self.category.attributes.prefetch_related('options').filter(display_type__gte=2)
        else:
            attrs = Attribute.objects.prefetch_related('options', 'categories').filter(display_type__gte=3,
                                                                                       categories__sex=self.sex).distinct()
        attrs_dict = {'color': [], 'size': [], 'style': [], 'text': []}
        for attr in attrs:
            attrs_dict[attr.attr_type].append(attr)

        self.attrs = attrs_dict
        return self.attrs

    def get_context_data(self, **kwargs):
        category = self.get_category()
        products = self.get_queryset()
        context = {
            'category': category,
            'sex': self.sex,
            'categories': Category.objects.filter(sex=self.sex),
            'products': products,
            'attrs': self.get_attributes(),
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
        _attrs = self.product.attributes.prefetch_related('options').filter(display_type__gte=1)

        attrs = {'color': [], 'size': [], 'style': [], 'text': []}
        attrs_dict = {}
        attrs_ids = []
        for attr in _attrs:
            attrs[attr.attr_type].append(attr)
            attrs_dict[attr.id] = attr
            attrs_ids.append(attr.id)

        self.attrs = attrs
        self.attrs_dict = attrs_dict
        self.attrs_ids = attrs_ids

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
