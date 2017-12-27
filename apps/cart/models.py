# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models

from ..catalog.models import Product, ProductOption


class Cart(models.Model):
    STATUS_CHOICES = (
        (0, 'новый'),
        (1, 'принят'),
        (2, 'отправлен'),
        (3, 'исполнен'),
        (4, 'отменен'),
    )
    # DELIVERY_CHOICES = (
    #     ('0', 'Самовывоз'),
    #     ('1', 'Курьерская доставка'),
    #     ('2', 'Отправление первого класса'),
    #     ('3', 'Почта'),
    # )
    # PAYMENT_CHOICES = (
    #     ('0', 'Пластиковые карты'),
    #     ('1', 'Наличные'),
    #     ('2', 'Долг по дружбе'),
    # )
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Профиль', blank=True, null=True)

    creation_date = models.DateTimeField('Дата создания', auto_now_add=True)
    checked_out = models.BooleanField('Корзина оформлена', default=False)
    checkout_date = models.DateTimeField('Дата оформления', null=True, blank=True)

    # postal_code = models.CharField('Почтовый код', max_length=255, null=True, blank=True)
    country = models.CharField('Страна', max_length=225, null=True, blank=True)
    city = models.CharField('Город', max_length=225, null=True, blank=True)
    address = models.TextField('Адрес', null=True, blank=True)
    phone = models.CharField('Телефон', max_length=30, null=True, blank=True)
    fio = models.CharField('Имя, Фамилия, Отчество', max_length=512, null=True, blank=True)

    # tracking_number = models.CharField('Номер отслеживания', max_length=255, null=True, blank=True)
    # delivery_type = models.CharField('Тип доставки', max_length=15, choices=DELIVERY_CHOICES, null=True, blank=True)
    # payment_type = models.CharField('Тип оплаты', max_length=15, choices=PAYMENT_CHOICES, null=True, blank=True)

    status = models.PositiveSmallIntegerField('Статус', choices=STATUS_CHOICES, default=0)
    summary = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ('-creation_date',)

    def __unicode__(self):
        return unicode(self.creation_date)

    def save(self, *args, **kwargs):
        if not self.checked_out:
            self.summary = self.get_summary()
        return super(Cart, self).save(*args, **kwargs)

    def count(self):
        count_list = self.cartitem_set.all().values_list('count', flat=True)
        result = sum(count_list)
        return result
    count.allow_tags = True
    count.short_description = 'Количество товара'

    def get_summary(self):
        price_list = self.cartitem_set.all().values_list('price', flat=True)
        result = sum(price_list)
        return result

    # # def get_order_url(self):
    # #     return reverse('profile:order', kwargs={'pk': self.id})

    def show_profile(self):
        return self.profile or ''
    show_profile.allow_tags = True
    show_profile.short_description = 'Клиент'

    def _show_value(self, value):
        value = int(value) if int(value) == value else value
        return '{0:,}'.format(value).replace(',', ' ')

    def show_summary(self):
        return self._show_value(self.summary)

    def get_order_id(self):
        return '{0:06}'.format(self.id)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart)
    product = models.ForeignKey(Product, verbose_name='Товар')
    option = models.ForeignKey(ProductOption, verbose_name='Вариант')
    count = models.PositiveIntegerField('Количество')

    attrs = JSONField(default=dict)
    extra_products = JSONField(default=dict)

    option_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    extra_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    wrapping_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ('cart', '-id',)

    def __unicode__(self):
        return '{} units of {}'.format(self.count, self.product.title)

    @property
    def base_price(self):
        return self.option_price+self.extra_price

    def count_price(self):
        return self.base_price*self.count + self.wrapping_price

    def save(self, *args, **kwargs):
        self.price = self.count_price()
        return super(CartItem, self).save(*args, **kwargs)

    @property
    def price_int(self):
        price = self.price
        int_value = int(price)
        return (int_value if int_value == price
                else int_value + 1)
