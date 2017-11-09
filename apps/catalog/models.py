# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.safestring import mark_safe

from ckeditor_uploader.fields import RichTextUploadingField
from colorfield.fields import ColorField
from easy_thumbnails.fields import ThumbnailerImageField
from sortedm2m.fields import SortedManyToManyField

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
    title = models.CharField('Название', max_length=255)
    slug = models.SlugField('В URL', help_text='''уникальное поле; принимаются английские буквы, цифры и символ "_"
                                                  <br><br>примеры:<br>- color<br>- top_w<br>- bottom_size''', unique=True)
    attr_type = models.CharField('Тип', max_length=7, choices=ATTRIBUTE_TYPES)
    position = models.CharField('Расположение', max_length=7, choices=POSITION_CHOICES, default='all')
    order = models.IntegerField('Порядок', default=10)
    display_type = models.SmallIntegerField('Тип показа', choices=DISPLAY_TYPES, default=3)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'атрибут'
        verbose_name_plural = 'атрибуты'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = (self.slug or '').replace('-', '_')
        return super(Attribute, self).save(*args, **kwargs)

    @mark_safe
    def options_instruction(self):
        return 'для заполнения вариантов сначала сохраните объект'
    options_instruction.allow_tags = True
    options_instruction.short_description = 'Варианты'


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
            if not attr_type == 'style':
                self.picture = ''
        return super(AttributeOption, self).save(*args, **kwargs)

    def get_placeholder_image(self, image_attrs='', dimension=25, image_src=''):
        if not image_src:
            image_src = 'http://via.placeholder.com/{}/{}'.format(dimension, image_attrs)
        return '''<img src="{}"
                       style="border-radius: {}px; border: 1px solid black"
                       title="{}">'''.format(image_src, dimension, self.title)

    @property
    def picture_url(self):
        return self.picture['attribute_option'].url if self.picture else ''

    def get_label(self, attr_type=None):
        attr_type = attr_type or self.attribute.attr_type
        label = (self.get_placeholder_image('{0}/{0}'.format(self.color[1:]))
                     if (attr_type == 'color' and self.color)
                 else self.get_placeholder_image('ffffff/000000/?text={}'.format(self.title), 45)
                     if attr_type == 'size'
                 else self.get_placeholder_image(image_src=self.picture_url, dimension=37)
                     if (attr_type == 'style' and self.picture)
                 else self.title)
        return mark_safe(label)


# === Категории ===

class Category(MetatagModel):
    SEX_CHOICES = (
        ('male', 'Мужчинам'),
        ('female', 'Женщинам'),
    )
    title = models.CharField('Название', max_length=255)
    sex = models.CharField('Пол', max_length=7, choices=SEX_CHOICES, default='female')
    order = models.IntegerField('Порядок', default=10)
    attributes = SortedManyToManyField(Attribute, verbose_name='Атрибуты', related_name='categories', blank=True)

    class Meta:
        ordering = ['sex', 'order', 'id', ]
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __unicode__(self):
        return self.title

    def show_sex(self):
        return {
            'male': 'М',
            'female': 'Ж',
        }.get(self.sex, '')
    show_sex.allow_tags = True
    show_sex.short_description = 'Пол'

    def show_attributes(self):
        return list(self.attributes.values_list('title', flat=True))
    show_attributes.allow_tags = True
    show_attributes.short_description = 'Атрибуты'

    @property
    def attrs_list(self):
        attrs = self.attributes.prefetch_related('options').all()
        attrs = [{
            'title': attr.title,
            'slug': attr.slug,
            'choices': [(option.id, option.get_label(attr_type=attr.attr_type)) for option in attr.options.all()],
        } for attr in attrs]
        return attrs

    @property
    def attrs_slugs(self):
        return list(self.attributes.values_list('slug', flat=True))


# === Дополнительные товары + сертификаты ===

class AdditionalProduct(models.Model):
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


# === Товары ===

class Product(MetatagModel):
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products')
    title = models.CharField('Название', max_length=255)
    subtitle = models.CharField('Подзаголовок', max_length=255, blank=True)
    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    photo = ThumbnailerImageField('Фото', upload_to='catalog/products/')
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    text = RichTextUploadingField('Текст', blank=True, null=True)
    in_stock = models.SmallIntegerField('Количество на складе', default=5)

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

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __unicode__(self):
        return self.title

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
        return self.photo['product_cover'].url if self.photo else ''

    def get_price_rub(self):
        price = self.price_rub
        return int(price) if int(price) == price else price

    @mark_safe
    def options_instruction(self):
        return 'для заполнения вариантов сначала сохраните объект'
    options_instruction.allow_tags = True
    options_instruction.short_description = 'Варианты товара'

    @mark_safe
    def photos_instruction(self):
        return 'для добавления фото сначала сохраните объект'
    photos_instruction.allow_tags = True
    photos_instruction.short_description = 'Фото'

    @mark_safe
    def show_category(self):
        return '{} (<a href="/admin/catalog/product/{}/change_category/">изменить</a>)'.format(
            self.category.__unicode__(), self.id
        )
    show_category.allow_tags = True
    show_category.short_description = 'Категория'

    def set_attrs(self):
        attrs = {slug: [] for slug in self.category.attrs_slugs}
        for _attrs in self.options.values_list('attrs', flat=True):
            for k, v in _attrs.iteritems():
                if isinstance(v, list):
                    attrs[k].extend(v)
        attrs = {k: list(set(v)) for k, v in attrs.iteritems()}
        self.attrs = attrs
        self.save()


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


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='photos')
    photo = ThumbnailerImageField('Фото', upload_to='catalog/products/')
    attrs = JSONField(default=dict)

    class Meta:
        ordering = ['id', ]
        verbose_name = 'фото'
        verbose_name_plural = 'фото'

    def __unicode__(self):
        return '#{}: {}'.format(self.id, self.photo.name)
