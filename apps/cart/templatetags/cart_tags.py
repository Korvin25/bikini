# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from django import template
from django.conf import settings

from apps.catalog.models import Attribute, AttributeOption, ExtraProduct


register = template.Library()


@register.simple_tag()
def get_attribute(slug):
    attribute = Attribute.objects.filter(slug=slug).first()
    return attribute


@register.simple_tag()
def get_option(attr, option_id):
    option = AttributeOption.objects.filter(attribute_id=attr.id, id=option_id).first()
    return option


@register.simple_tag()
def get_extra_product(extra_product_id):
    extra_p = ExtraProduct.objects.filter(id=extra_product_id).first()
    return extra_p


# @register.filter
# def get_photo_url(option, product):
#     slug = option.attribute.slug
#     q = {'attrs__{}__contains'.format(slug): option.id}
#     photo = product.photos.filter(**q).first()
#     # import ipdb; ipdb.set_trace()
#     return (photo.style_photo_url if photo
#             else option.style_photo_url)


# @register.filter
# def get_product_url(product, category_or_sex=None):
#     category = sex = None
#     if isinstance(category_or_sex, Category):
#         category = category_or_sex
#     else:
#         sex = category_or_sex
#     return product.get_absolute_url(category=category, sex=sex)


# @register.filter
# def get_product_meta_title(product, category=None):
#     return product.get_meta_title(category=category)


# @register.filter
# def had_neighbor(attr, attr_ids):
#     neighbors_ids = attr['attr'].from_neighbor.all().values_list('id', flat=True)
#     return True if (set(neighbors_ids) & set(attr_ids)) else False


# @register.simple_tag
# def item_extra_products_str(item):
#     pieces = []
#     extra_products_ids = item.extra_products.keys()
#     pieces = ['+ {}'.format(extra_p.title) for extra_p in ExtraProduct.objects.filter(id__in=extra_products_ids)]
#     return '<br/>'.join(pieces)


# @register.simple_tag
# def item_color(item, color_attribute):
#     option = None
#     color_option_id = item.attrs.get('color')

#     if color_option_id:
#         try:
#             option = AttributeOption.objects.get(attribute_id=color_attribute.id, id=color_option_id)
#         except AttributeOption.DoesNotExist:
#             pass

#     return option
