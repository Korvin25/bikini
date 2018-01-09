# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe

from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor.fields import RichTextField
from colorfield.fields import ColorField
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer
from filer.fields.image import FilerImageField
from sortedm2m.fields import SortedManyToManyField
from tinymce.models import HTMLField

from ..core.utils import with_watermark
from ..settings.models import MetatagModel


# === Атрибуты (справочники) ===

class Attribute(models.Model):
    ATTRIBUTE_TYPES = (
        ('color', 'цвет'),
        ('size', 'размер'),
        ('style', 'фасон'),
        ('text', 'текст'),
    )
    POSITION_CHOICES = (
        ('all', 'все'),
        ('bottom', 'низ'),
        ('top', 'верх'),
    )
    DISPLAY_TYPES = (
        (3, 'в общем фильтре'),
        (2, 'в фильтре категории'),
        (1, 'на странице товара'),
        (0, 'откл.'),
    )
    CATEGORY_CHOICES = (
        ('primary', 'основные'),
        ('extra', 'дополнительные'),
    )
    admin_title = models.CharField('Название (в админке)', max_length=255)
    title = models.CharField('Название (на сайте)', max_length=255)
    slug = models.SlugField('В URL', help_text='''уникальное поле; принимаются английские буквы, цифры и символ "_"
                                                  <br><br>примеры:<br>- color<br>- top_w<br>- bottom_size''', unique=True)
    attr_type = models.CharField('Тип', max_length=7, choices=ATTRIBUTE_TYPES)
    neighbor = models.ForeignKey('self', verbose_name='Соседний атрибут', null=True, blank=True,
                                 limit_choices_to={'attr_type': 'size'},
                                 help_text='выводится рядом на странице товара', related_name='from_neighbor')
    category = models.CharField('Категория', max_length=7, choices=CATEGORY_CHOICES)
    display_type = models.SmallIntegerField('Тип показа', choices=DISPLAY_TYPES, default=3)
    order = models.IntegerField('Порядок', default=10)

    # old and unused:
    position = models.CharField('Расположение', max_length=7, choices=POSITION_CHOICES, default='all')
    add_to_price = models.BooleanField('Прибавлять к цене', default=False, help_text='для дополнительных атрибутов')

    class Meta:
        ordering = ['-category', 'order', 'id', ]
        verbose_name = 'атрибут'
        verbose_name_plural = 'атрибуты'

    def __unicode__(self):
        return self.admin_title

    def save(self, *args, **kwargs):
        self.slug = (self.slug or '').replace('-', '_')
        if self.category == 'extra' and self.display_type > 1:
            self.display_type = 1
        return super(Attribute, self).save(*args, **kwargs)

    def set_neighbor(self, obj):
        """
        Реализуем аналог symmetrical=True у OneToOneField
        """
        self.neighbor = obj
        self.save()

    @mark_safe
    def options_instruction(self):
        return 'для заполнения вариантов сначала сохраните объект'
    options_instruction.allow_tags = True
    options_instruction.short_description = 'Варианты'

    @classmethod
    def get_attrs_list(cls, qs):
        attrs = qs.prefetch_related('options').all()
        attrs = [{
            'title': attr.admin_title,
            'slug': attr.slug,
            'choices': [(option.id, option.get_label(attr_type=attr.attr_type)) for option in attr.options.all()],
        } for attr in attrs]
        return attrs


class AttributeOption(models.Model):
    attribute = models.ForeignKey(Attribute, verbose_name='Атрибут', related_name='options')
    title = models.CharField('Название', max_length=255)
    picture = ThumbnailerImageField('Картинка', upload_to='catalog/attributes/', blank=True)
    color = ColorField('Цвет', blank=True)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'вариант'
        verbose_name_plural = 'варианты'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.attribute:
            attr_type = self.attribute.attr_type
            if not attr_type == 'color':
                self.color = ''
            if not attr_type in ['style', 'color']:
                self.picture = ''
        return super(AttributeOption, self).save(*args, **kwargs)

    def get_placeholder_image(self, image_attrs='', dimension=35, image_src='', border=True):
        if not image_src:
            image_src = 'http://via.placeholder.com/{}/{}'.format(dimension, image_attrs)
        style = 'border-radius: {}px'.format(dimension)
        if border:
            style = '{}; border: 1px solid black'.format(style)
        return '''<img src="{0}"
                       style="height: {1}px; width: {1}px; {2}"
                       title="{3}">'''.format(image_src, dimension, style, self.title)

    @property
    def admin_picture_url(self):
        return self.picture['admin_attribute_option'].url if self.picture else ''

    @mark_safe
    def admin_show_picture(self):
        return (self.get_placeholder_image(image_src=self.admin_picture_url, dimension=200, border=False)
                if self.picture else '-')
    admin_show_picture.allow_tags = True
    admin_show_picture.short_description = 'Превью'

    @property
    def picture_url(self):
        return self.picture['attribute_option'].url if self.picture else ''

    @property
    def detail_picture_url(self):
        return self.picture['attribute_option_detail'].url if self.picture else ''

    def get_label(self, attr_type=None):
        attr_type = attr_type or self.attribute.attr_type
        label = (self.get_placeholder_image(image_src=self.admin_picture_url, dimension=35)
                     if (attr_type == 'color' and self.picture)
                 else self.get_placeholder_image('{0}/{0}'.format(self.color[1:]))
                     if (attr_type == 'color' and self.color)
                 else self.get_placeholder_image('ffffff/000000/?text={}'.format(self.title), 45)
                     if attr_type == 'size'
                 else self.get_placeholder_image(image_src=self.admin_picture_url, dimension=200, border=False)
                     if (attr_type == 'style' and self.picture)
                 else self.title)
        if self.color or self.picture:
            label = '{}&nbsp;&nbsp;{}'.format(label, self.title)
        return mark_safe(label)

    @property
    def style_photo_url(self):
        return self.picture['product_style'].url if self.picture else ''

    # @property
    # def color_style(self):
    #     style = ('background: url("{}");'.format(self.picture_url) if self.picture
    #              else 'background-color: {};'.format(self.color))
    #     return mark_safe(style)


class ExtraProduct(models.Model):
    admin_title = models.CharField('Название (в админке)', max_length=255)
    title = models.CharField('Название (на сайте)', max_length=255)
    slug = models.SlugField('В URL', help_text='''уникальное поле; принимаются английские буквы, цифры и символ "_"
                                                  <br><br>примеры:<br>- color<br>- top_w<br>- bottom_size''', unique=True)
    order = models.IntegerField('Порядок', default=10)
    attributes = SortedManyToManyField(Attribute, verbose_name='Атрибуты', related_name='extra_products',
                                       limit_choices_to={'category': 'extra'})

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'дополнительный товар'
        verbose_name_plural = 'атрибуты: дополнительные товары'

    def __unicode__(self):
        return self.admin_title

    def save(self, *args, **kwargs):
        self.slug = (self.slug or '').replace('-', '_')
        return super(ExtraProduct, self).save(*args, **kwargs)

    def show_attributes(self):
        return list(self.attributes.values_list('admin_title', flat=True))
    show_attributes.allow_tags = True
    show_attributes.short_description = 'Атрибуты'

    def get_attributes_qs(self):
        return self.attributes.filter(category='extra')

    def get_attrs_list(self):
        qs = self.get_attributes_qs()
        attrs = Attribute.get_attrs_list(qs)
        return attrs

    def get_attrs_slugs(self):
        qs = self.get_attributes_qs()
        return list(qs.values_list('slug', flat=True))

    @classmethod
    def get_all_attributes_qs(cls, qs=None):
        qs = qs or ExtraProduct.objects.all()
        return Attribute.objects.filter(extra_products__in=qs)

    @classmethod
    def get_all_attrs_list(cls, qs=None):
        qs = cls.get_all_attributes_qs(qs)
        attrs = Attribute.get_attrs_list(qs)
        return attrs

    @classmethod
    def get_all_attrs_slugs(cls, qs=None):
        qs = cls.get_all_attributes_qs(qs)
        return list(qs.values_list('slug', flat=True))


# === Категории ===

class Category(MetatagModel):
    SEX_CHOICES = (
        ('female', 'Женщинам'),
        ('male', 'Мужчинам'),
    )
    title = models.CharField('Название', max_length=255)
    slug = models.SlugField('В URL', max_length=127)
    sex = models.CharField('Пол', max_length=7, choices=SEX_CHOICES, default='female')
    order = models.IntegerField('Порядок', default=10)
    attributes = SortedManyToManyField(Attribute, verbose_name='Атрибуты', related_name='categories', blank=True,
                                       limit_choices_to={'category': 'primary'})

    class Meta:
        unique_together = [('sex', 'slug')]
        ordering = ['sex', 'order', 'id', ]
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __unicode__(self):
        return '({}) {}'.format(self.show_sex(), self.title)

    def get_absolute_url(self):
        reverse_name = {
            'female': 'women_category',
            'male': 'men_category',
        }.get(self.sex, '')
        return reverse(reverse_name, kwargs={'slug': self.slug})

    def get_title(self):
        SEX_TITLES = {
            'female': 'Женщинам',
            'male': 'Мужчинам',
        }
        return '{} — {}'.format(self.title, SEX_TITLES.get(self.sex))

    def show_sex(self):
        return {
            'female': 'Ж',
            'male': 'М',
        }.get(self.sex, '')
    show_sex.allow_tags = True
    show_sex.short_description = 'Пол'

    def show_attributes(self):
        return list(self.attributes.values_list('admin_title', flat=True))
    show_attributes.allow_tags = True
    show_attributes.short_description = 'Атрибуты'

    def get_attributes_qs(self, filter='primary'):
        # filter in ['primary', 'photos',]
        qs = self.attributes
        qs = (qs.filter(category='primary') if filter == 'primary'
              # else qs.filter(category='extra') if filter == 'extra'
              else qs.filter(attr_type__in=['color', 'style']) if filter == 'photos'
              else qs)
        return qs

    def get_attrs_list(self, filter='primary'):
        qs = self.get_attributes_qs(filter=filter)
        attrs = Attribute.get_attrs_list(qs)
        return attrs

    def get_attrs_slugs(self, filter='primary'):
        qs = self.get_attributes_qs(filter=filter)
        return list(qs.values_list('slug', flat=True))


# === Дополнительные товары + сертификаты ===

class AdditionalProduct(models.Model):
    """
    switched off
    """
    title = models.CharField('Название', max_length=255)
    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    photo = ThumbnailerImageField('Фото', upload_to='catalog/products/', blank=True)
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    show = models.BooleanField('Показывать на сайте', default=True)

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'дополнительный товар'
        verbose_name_plural = 'товары: дополнительные товары'

    def __unicode__(self):
        return self.title

    @property
    def price(self):
        # TODO
        return self.price_rub


class Certificate(models.Model):
    title = models.CharField('Название', max_length=255)
    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    show = models.BooleanField('Показывать на сайте', default=True)

    class Meta:
        ordering = ['price_rub', 'id', ]
        verbose_name = 'сертификат'
        verbose_name_plural = 'товары: сертификаты'

    def __unicode__(self):
        return self.title

    @property
    def price(self):
        # TODO
        return self.price_rub


class GiftWrapping(models.Model):
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'подарочная упаковка'
        verbose_name_plural = 'подарочная упаковка'

    def __unicode__(self):
        return '#1'

    def show_name(self):
        return 'Подарочная упаковка'
    show_name.allow_tags = True
    show_name.short_description = ''

    @classmethod
    def get_price(cls):
        obj = cls.objects.first()
        # TODO: eur, usd
        return obj.price_rub if obj else 200.0


# === Товары ===

class Product(MetatagModel):
    categories = models.ManyToManyField(Category, verbose_name='Категории', related_name='products')
    title = models.CharField('Название', max_length=255)
    subtitle = models.CharField('Подзаголовок', max_length=255, blank=True)
    slug = models.SlugField('В URL', max_length=127)
    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    # photo = ThumbnailerImageField('Фото', upload_to='catalog/products/')
    photo_f = FilerImageField(verbose_name='Фото')
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    text = RichTextUploadingField('Текст', blank=True, null=True)
    # text = RichTextField('Текст', blank=True, null=True)
    # text = HTMLField('Текст', blank=True, null=True)
    in_stock = models.SmallIntegerField('Количество на складе', default=5)

    order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, verbose_name=mark_safe('&nbsp;&nbsp;&nbsp;&nbsp;'))
    show = models.BooleanField('Показывать на сайте', default=True)
    show_at_homepage = models.BooleanField('Показывать на главной', default=False)
    order_at_homepage = models.IntegerField('Порядок на главной', default=10)
    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)

    attrs = JSONField(default=dict)

    additional_products = models.ManyToManyField(AdditionalProduct, blank=True,
                                                 verbose_name='Дополнительные товары', related_name='from_additional')
    associated_products = models.ManyToManyField('self', symmetrical=False, blank=True,
                                                 verbose_name='Сопутствующие товары', related_name='from_associated')
    also_products = models.ManyToManyField('self', symmetrical=False, blank=True,
                                           verbose_name='С этим товаром также покупают', related_name='from_also')

    attributes = SortedManyToManyField(Attribute, verbose_name='Атрибуты', related_name='products', blank=True,
                                       limit_choices_to={'category': 'primary'})

    class Meta:
        ordering = ['order', '-id', ]
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __unicode__(self):
        return self.title

    # def save(self, *args, **kwargs):
    #     init_attributes = (True if (not self.id and getattr(self, 'category', None))
    #                       else False)
    #     s = super(Product, self).save(*args, **kwargs)
    #     if init_attributes:
    #         self.set_attributes_from_category(self.category)
    #     return s

    def get_absolute_url(self, category=None, sex=None):
        category = category or (self.categories.first() if not sex else self.categories.filter(sex=sex).first())
        return ('{}{}-{}/'.format(category.get_absolute_url(), self.slug, self.id) if category
                else None)

    # def get_title(self):
    #     return '{} — {}'.format(self.title, self.category.get_title())

    def get_meta_title(self, category=None):
        title = self.title
        if self.meta_title:
            title = self.meta_title
        else:
            category = category or self.categories.first()
            title = '{} — {} — Bikinimini.ru'.format(self.title, category.get_title())
        return title

    # def set_attributes_from_category(self, category):
    #     self.attributes = category.attributes.all()
    #     self.set_attrs()

    def set_attributes_from_categories(self, categories_ids):
        self.attributes = Attribute.objects.filter(categories__id__in=categories_ids).distinct()
        self.set_attrs()

    def create_extra_products(self, extra_products_ids):
        extra_options_ids = []
        extra_products = ExtraProduct.objects.filter(id__in=extra_products_ids)
        for ep in extra_products:
            eo, _created = ProductExtraOption.objects.get_or_create(product_id=self.id, extra_product_id=ep.id,
                                                                    defaults={'title': ep.admin_title})
            extra_options_ids.append(eo.id)
        self.extra_options.exclude(id__in=extra_options_ids).delete()

    def has_attrs(self):
        return ('<img src="/static/admin/img/icon-yes.svg" alt="True">' if self.attrs
                else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    has_attrs.allow_tags = True
    has_attrs.short_description = 'Есть атрибуты?'

    @property
    def price(self):
        # TODO
        return self.price_rub

    @property
    def cover_thumb(self):
        # return self.photo['product_cover'].url
        return get_thumbnailer(self.photo_f)['product_cover'].url

    @property
    def cart_cover_thumb(self):
        return get_thumbnailer(self.photo_f)['cart_product_cover'].url

    @property
    def preview_url(self):
        # return self.photo['product_photo_preview'].url
        return with_watermark(get_thumbnailer(self.photo_f)['product_photo_preview'].url)

    @property
    def thumb_url(self):
        # return self.photo['product_photo_thumb'].url
        return get_thumbnailer(self.photo_f)['product_photo_thumb'].url

    @property
    def big_url(self):
        # return self.photo['product_photo_big'].url
        return with_watermark(get_thumbnailer(self.photo_f)['product_photo_big'].url)

    def get_price_rub(self):
        price = self.price_rub
        return int(price) if int(price) == price else price

    @mark_safe
    def options_instruction(self):
        return 'для заполнения вариантов сначала сохраните объект'
    options_instruction.allow_tags = True
    options_instruction.short_description = 'Варианты товара'

    @mark_safe
    def extra_options_instruction(self):
        if self.id:
            return '''для заполнения дополнительных товаров сначала выберите их на
                      <a href="/admin/catalog/product/{}/change_attributes/">странице изменения атрибутов</a>'''.format(self.id)
        else:
            return '''для заполнения дополнительных товаров сначала сохраните объект,
                      а потом выберите их на странице изменения атрибутов'''.format(self.id)
    extra_options_instruction.allow_tags = True
    extra_options_instruction.short_description = 'Дополнительные товары'

    @mark_safe
    def photos_instruction(self):
        return 'для добавления фото сначала сохраните объект'
    photos_instruction.allow_tags = True
    photos_instruction.short_description = 'Фото'

    @mark_safe
    def list_categories(self):
        return ', '.join([cat.__unicode__() for cat in self.categories.all()]) or '-'
    list_categories.allow_tags = True
    list_categories.short_description = 'Категории'

    @mark_safe
    def show_categories(self):
        if self.id:
            return '{} (<a href="/admin/catalog/product/{}/change_categories/">изменить</a>)'.format(
                self.list_categories(), self.id
            )
        else:
            return '-'
    show_categories.allow_tags = True
    show_categories.short_description = 'Категории'

    # @mark_safe
    # def show_category(self):
    #     if self.id:
    #         return '{} (<a href="/admin/catalog/product/{}/change_category/">изменить</a>)'.format(
    #             self.category.__unicode__(), self.id
    #         )
    #     else:
    #         return '-'
    # show_category.allow_tags = True
    # show_category.short_description = 'Категория'

    @mark_safe
    def show_attributes(self):
        attrs_str = list(self.attributes.values_list('admin_title', flat=True))
        return '{} (<a href="/admin/catalog/product/{}/change_attributes/">изменить</a>)'.format(attrs_str, self.id)
    show_attributes.allow_tags = True
    show_attributes.short_description = 'Атрибуты'

    def get_attributes_qs(self, filter='primary'):
        # filter in ['primary', 'photos',]
        qs = Attribute.objects.none()
        if filter == 'primary':
            qs = self.attributes
            qs = qs.filter(category='primary')
        elif filter == 'photos':
            attrs_ids = set(self.attributes.values_list('id', flat=True))
            extra_attrs_ids = set(self.extra_products.values_list('extra_product__attributes', flat=True))
            qs_ids = attrs_ids | extra_attrs_ids
            qs = Attribute.objects.filter(id__in=qs_ids)
            qs = qs.filter(attr_type__in=['color', 'style'])
        return qs

    def get_attrs_list(self, filter='primary'):
        qs = self.get_attributes_qs(filter=filter)
        attrs = Attribute.get_attrs_list(qs)
        return attrs

    def get_attrs_slugs(self, filter='primary'):
        qs = self.get_attributes_qs(filter=filter)
        return list(qs.values_list('slug', flat=True))

    def set_attrs(self):
        attrs = {slug: [] for slug in self.get_attrs_slugs()}
        for _attrs in self.options.values_list('attrs', flat=True):
            for k, v in _attrs.iteritems():
                if isinstance(v, list):
                    if k in attrs:
                        attrs[k].extend(v)
        attrs = {k: list(set(v)) for k, v in attrs.iteritems()}
        self.attrs = attrs
        self.save()

    def get_placeholder_image(self, image_attrs='', dimension=35, image_src='', border=True):
        if not image_src:
            image_src = 'http://via.placeholder.com/{}/{}'.format(dimension, image_attrs)
        style = 'border-radius: {}px'.format(dimension)
        if border:
            style = '{}; border: 1px solid black'.format(style)
        return '''<img src="{0}"
                       style="height: {1}px; width: {1}px; {2}"
                       title="{3}">'''.format(image_src, dimension, style, self.title)

    # @property
    # def admin_photo_url(self):
    #     return self.photo['admin_product_photo'].url if self.photo else ''

    # @mark_safe
    # def admin_show_photo(self):
    #     return ('<a href="{}" target="_blank"><img src="{}"></a>'.format(self.photo.url, self.admin_photo_url)
    #             if self.photo else '-')
    # admin_show_photo.allow_tags = True
    # admin_show_photo.short_description = 'Превью'

    @property
    def extra_products(self):
        extra_products = self.extra_options.prefetch_related('extra_product', 'extra_product__attributes').all()
        # return [extra_p for extra_p in extra_products if extra_p.attrs]
        return extra_products.filter(attrs__gt={})

    @property
    def attrs_json(self):
        return json.dumps(self.attrs)


class ProductOption(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='options')
    title = models.CharField('Название', max_length=255)

    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0,
                                    help_text='оставьте цены пустыми, чтобы использовать цену родительского товара')
    in_stock = models.SmallIntegerField('Количество на складе', default=5)

    attrs = JSONField(default=dict)

    class Meta:
        ordering = ['id', ]
        verbose_name = 'вариант'
        verbose_name_plural = 'варианты товара'

    def __unicode__(self):
        return self.title

    @property
    def price(self):
        # TODO
        return self.price_rub


class ProductExtraOption(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='extra_options')
    extra_product = models.ForeignKey(ExtraProduct, verbose_name='Дополнительный товар', related_name='extra_options')
    title = models.CharField('Название', max_length=255)

    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    in_stock = models.SmallIntegerField('Количество на складе', default=5)

    attrs = JSONField(default=dict)

    class Meta:
        unique_together = [('product', 'extra_product')]
        ordering = ['id', ]
        verbose_name = 'дополнительный товар'
        verbose_name_plural = 'дополнительные товары'

    def __unicode__(self):
        return self.title

    @mark_safe
    def attrs_instruction(self):
        return 'для заполнения атрибутов сначала выберите тип дополнительного товара и сохраните объект'
    attrs_instruction.allow_tags = True
    attrs_instruction.short_description = 'Атрибуты'

    @property
    def price(self):
        # TODO
        return self.price_rub


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='photos')
    title = models.CharField('Название', blank=True, max_length=255, help_text='необязательно; для показа в админке')
    # photo = ThumbnailerImageField('Фото', upload_to='catalog/products/')
    photo_f = FilerImageField(verbose_name='Фото')
    attrs = JSONField(default=dict)

    class Meta:
        ordering = ['id', ]
        verbose_name = 'фото'
        verbose_name_plural = 'фото'

    def __unicode__(self):
        return '#{}: {}'.format(self.id, self.title or self.photo_f.original_filename)

    @property
    def preview_url(self):
        # return self.photo['product_photo_preview'].url
        return with_watermark(get_thumbnailer(self.photo_f)['product_photo_preview'].url)

    @property
    def thumb_url(self):
        # return self.photo['product_photo_thumb'].url
        return get_thumbnailer(self.photo_f)['product_photo_thumb'].url

    @property
    def big_url(self):
        # return self.photo['product_photo_big'].url
        return with_watermark(get_thumbnailer(self.photo_f)['product_photo_big'].url)

    @property
    def style_photo_url(self):
        # return self.photo['product_style'].url
        return get_thumbnailer(self.photo_f)['product_style'].url

    @property
    def attrs_json(self):
        return json.dumps(self.attrs)

    # @property
    # def admin_photo_url(self):
    #     return self.photo['admin_product_photo'].url if self.photo else ''

    # @mark_safe
    # def admin_show_photo(self):
    #     return ('<a href="{}" target="_blank"><img src="{}"></a>'.format(self.photo.url, self.admin_photo_url)
    #             if self.photo else '-')
    # admin_show_photo.allow_tags = True
    # admin_show_photo.short_description = 'Превью'
