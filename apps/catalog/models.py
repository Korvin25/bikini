# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField
from easy_thumbnails.fields import ThumbnailerImageField
# from multiselectfield import MultiSelectField

from ..settings.models import MetatagModel


class Category(MetatagModel):
    SEX_CHOICES = (
        ('male', 'Мужчинам'),
        ('female', 'Женщинам'),
    )
    title = models.CharField('Название', max_length=255)
    # sex = MultiSelectField('Пол', max_length=15, choices=SEX_CHOICES)
    sex = models.CharField('Пол', max_length=7, choices=SEX_CHOICES, default='female')
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['sex', 'order', 'id', ]
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __unicode__(self):
        return self.title


class Product(MetatagModel):
    PRODUCT_TYPES = (
        ('default', 'товар'),
        ('additional', 'дополнительный товар'),
        ('certificate', 'подарочный сертификат'),
    )
    categories = models.ManyToManyField(Category, verbose_name='Категории', related_name='products', blank=True)
    product_type = models.CharField('Тип товара', max_length=15, choices=PRODUCT_TYPES, default='default')
    title = models.CharField('Название', max_length=255)
    subtitle = models.CharField('Подзаголовок', max_length=255, blank=True)
    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    photo = ThumbnailerImageField('Фото', upload_to='catalog/products/')
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    text = RichTextUploadingField('Текст', blank=True, null=True)
    in_stock = models.SmallIntegerField('Количество на складе', default=1)

    show = models.BooleanField('Показывать на сайте', default=True)
    show_at_homepage = models.BooleanField('Показывать на главной', default=False)
    order_at_homepage = models.IntegerField('Порядок на главной', default=10)
    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)

    additional_products = models.ManyToManyField('self', symmetrical=False, blank=True,
                                                 verbose_name='Дополнительные товары', related_name='from_additional',
                                                 limit_choices_to={'product_type': 'additional'})
    associated_products = models.ManyToManyField('self', symmetrical=False, blank=True,
                                                 verbose_name='Сопутствующие товары', related_name='from_associated',
                                                 limit_choices_to={'product_type': 'default'})
    also_products = models.ManyToManyField('self', symmetrical=False, blank=True,
                                           verbose_name='С этим товаром также покупают', related_name='from_also',
                                           limit_choices_to={'product_type': 'default'})

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __unicode__(self):
        return self.title

    @property
    def price(self):
        # TODO
        return self.price_rub

    def show_categories(self):
        return ', '.join(self.categories.all().values_list('title', flat=True)) or '-'
    show_categories.allow_tags = True
    show_categories.short_description = 'Категории'

    @property
    def cover_thumb(self):
        return self.photo['product_cover'].url if self.photo else ''

    def get_price_rub(self):
        price = self.price_rub
        return int(price) if int(price) == price else price
