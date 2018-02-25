# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy

from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from ..catalog.models import Certificate, Product, ProductOption
from ..catalog.templatetags.catalog_tags import get_product_attrs_url
from ..geo.models import Country
from .utils import make_hash


def to_int_plus(value):
    int_value = int(value)
    return int_value if int_value == value else int_value + 1


class DeliveryMethod(models.Model):
    title = models.CharField('Название', max_length=511)
    short_title = models.CharField('Краткое название', max_length=63, blank=True, help_text='для вывода в личном кабинете')
    price_rub = models.DecimalField('Стоимость, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Стоимость, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Стоимость, usd.', max_digits=9, decimal_places=2, default=0)
    is_enabled = models.BooleanField('Включен?', default=True)
    order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, verbose_name=mark_safe('&nbsp;&nbsp;&nbsp;&nbsp;'))

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'способ доставки'
        verbose_name_plural = 'способы доставки'

    def __unicode__(self):
        return self.title

    def get_short_title(self):
        return self.short_title or self.title

    @property
    def price(self):
        # TODO
        return self.price_rub


class PaymentMethod(models.Model):
    title = models.CharField('Название', max_length=511)
    short_title = models.CharField('Краткое название', max_length=63, blank=True, help_text='для вывода в личном кабинете')
    is_paypal = models.BooleanField('Оплата через PayPal', default=False)
    is_enabled = models.BooleanField('Включен?', default=True)
    order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, verbose_name=mark_safe('&nbsp;&nbsp;&nbsp;&nbsp;'))

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'способ оплаты'
        verbose_name_plural = 'способы оплаты'

    def __unicode__(self):
        return self.title

    def get_short_title(self):
        return self.short_title or self.title


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
    country = models.ForeignKey(Country, verbose_name='Страна', null=True, blank=True)
    city = models.CharField('Город', max_length=225, null=True, blank=True)
    address = models.TextField('Адрес', null=True, blank=True)
    phone = models.CharField('Телефон', max_length=30, null=True, blank=True)
    name = models.CharField('Полное имя', max_length=511, null=True, blank=True)

    delivery_method = models.ForeignKey(DeliveryMethod, verbose_name='Способ доставки', null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, verbose_name='Способ оплаты', null=True, blank=True)
    additional_info = models.TextField('Дополнительная информация', blank=True)

    # tracking_number = models.CharField('Номер отслеживания', max_length=255, null=True, blank=True)
    # delivery_type = models.CharField('Тип доставки', max_length=15, choices=DELIVERY_CHOICES, null=True, blank=True)
    # payment_type = models.CharField('Тип оплаты', max_length=15, choices=PAYMENT_CHOICES, null=True, blank=True)

    status = models.PositiveSmallIntegerField('Статус', choices=STATUS_CHOICES, default=0)
    summary = models.DecimalField('Сумма, руб.', max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ('-creation_date',)

    def __unicode__(self):
        # return unicode(self.creation_date)
        return self.title

    def save(self, *args, **kwargs):
        if not self.checked_out:
            self.summary = self.get_summary()
        return super(Cart, self).save(*args, **kwargs)

    def count(self):
        count_list = self.cartitem_set.all().values_list('count', flat=True)
        result = sum(count_list) + self.certificatecartitem_set.count()
        return result
    count.allow_tags = True
    count.short_description = 'Количество товара'

    def get_summary(self):
        price_list = self.cartitem_set.all().values_list('price', flat=True)
        result = sum(price_list)
        certificate_price_list = self.certificatecartitem_set.all().values_list('price', flat=True)
        result += sum(certificate_price_list)
        delivery_method = self.delivery_method
        if delivery_method:
            result = result + delivery_method.price
        return result

    def is_order_with_discount(self):
        discounts = self.cartitem_set.all().values_list('discount', flat=True)
        with_discount = bool(sum(discounts))
        return ('<img src="/static/admin/img/icon-yes.svg" alt="Да">' if with_discount
                else '<img src="/static/admin/img/icon-no.svg" alt="Нет">')
    is_order_with_discount.allow_tags = True
    is_order_with_discount.short_description = 'Товары со скидкой'

    # # def get_order_url(self):
    # #     return reverse('profile:order', kwargs={'pk': self.id})

    def profile_with_link(self):
        p = self.profile
        if not p:
            return '-'
        link = '<a href="/admin/lk/profile/{}/change/" target="_blank">{}</a>'.format(p.id, p.__unicode__())
        return mark_safe(link)
    profile_with_link.allow_tags = True
    profile_with_link.short_description = 'Профиль'

    # def title_with_link(self):
    #     return '<a href="/admin/cart/cart/{}/change/" target="_blank">{}</a>'.format(self.id, self.title)
    # title_with_link.allow_tags = True
    # title_with_link.short_description = 'Заказ'

    def show_profile(self):
        return self.profile or ''
    show_profile.allow_tags = True
    show_profile.short_description = 'Клиент'

    def show_delivery_method(self):
        method = self.delivery_method
        return method.get_short_title() if method else '-'
    show_delivery_method.allow_tags = True
    show_delivery_method.short_description = 'Способ доставки'

    def show_payment_method(self):
        method = self.payment_method
        return method.get_short_title() if method else '-'
    show_payment_method.allow_tags = True
    show_payment_method.short_description = 'Способ оплаты'

    def _show_value(self, value):
        value = int(value) if int(value) == value else value
        return '{0:,}'.format(value).replace(',', ' ')

    def show_summary(self):
        return self._show_value(self.summary)

    def get_order_id(self):
        return '{0:06}'.format(self.id)

    @property
    def title(self):
        return '№ {}'.format(self.number)

    @property
    def number(self):
        # TODO: покрасивше
        if not self.id:
            return '0'
        if self.id > 1000:
            return '{:,}'.format(self.id).rjust(7, '0').replace(',', ' ')
        else:
            _number = '{:03}'.format(self.id)
            return '000 {}'.format(_number)

    def show_items(self):
        template = get_template('cart/include/cart_items.html')
        data = template.render({'cart': self})
        return mark_safe(data)
    show_items.allow_tags = True
    show_items.short_description = 'Список позиций'

    @property
    def cart_items(self):
        return self.cartitem_set.select_related('product', 'option').all()

    @property
    def certificate_items(self):
        return self.certificatecartitem_set.select_related('certificate').all()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, db_index=True)
    product = models.ForeignKey(Product, verbose_name='Товар', db_index=True)
    option = models.ForeignKey(ProductOption, verbose_name='Вариант')
    count = models.PositiveIntegerField('Количество')

    attrs = JSONField(default=dict)
    extra_products = JSONField(default=dict)
    hash = models.IntegerField(default=0, db_index=True)

    option_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    discount = models.PositiveSmallIntegerField(default=0)
    extra_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    wrapping_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ('cart', '-id',)

    def __unicode__(self):
        return '{} units of {}'.format(self.count, self.title)

    @property
    def title(self):
        return self.option.title or self.product.__unicode__()

    def get_vendor_code(self):
        return self.option.vendor_code or self.product.vendor_code

    @property
    def url(self):
        return get_product_attrs_url(self.product, self.attrs, self.extra_products, self.wrapping_price, self.count)

    @classmethod
    def had_discounts(cls, cart_ids):
        return bool(cls.objects.filter(cart_id__in=cart_ids, discount__gt=0).count())

    def get_base_price(self, with_discount=True):
        option_price = self.option_price
        if with_discount and self.discount:
            discount_price = option_price*self.discount // 100
            option_price = to_int_plus(option_price - discount_price)
        return option_price+self.extra_price

    @property
    def base_price(self):
        return self.get_base_price()

    @property
    def base_price_without_discount(self):
        return self.get_base_price(with_discount=False)

    def count_price(self):
        return (self.base_price*self.count + self.wrapping_price if self.count
                else 0)

    @property
    def total_price_without_discount(self):
        return to_int_plus(self.base_price_without_discount*self.count + self.wrapping_price if self.count
                           else 0)

    def set_hash(self):
        hash = 0
        if self.extra_products:
            x = copy.deepcopy(self.attrs)
            x.update(self.extra_products)
            hash = make_hash(x)
        else:
            hash = make_hash(self.attrs)
        self.hash = hash
        self.save()
        return hash

    def save(self, *args, **kwargs):
        self.price = self.count_price()
        return super(CartItem, self).save(*args, **kwargs)

    @property
    def price_int(self):
        price = self.price
        return to_int_plus(price)


class CertificateCartItem(models.Model):
    cart = models.ForeignKey(Cart)
    certificate = models.ForeignKey(Certificate, verbose_name='Сертификат', related_name='cart_items')

    recipient_name = models.CharField('Имя получателя', max_length=255)
    recipient_email = models.EmailField('Email получателя', blank=True)
    sender_name = models.CharField('Имя отправителя', max_length=255, blank=True)
    sender_phone = models.CharField('Телефон отправителя', max_length=127)
    sender_email = models.EmailField('Email отправителя')
    message = models.TextField('Сообщение получателю', blank=True)

    send_immediately = models.BooleanField('Отправлять сразу?', default=True)
    send_date = models.DateField('Дата отправки', blank=True, null=True)

    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'сертификат'
        verbose_name_plural = 'сертификаты'
        ordering = ('cart', '-id',)

    def __unicode__(self):
        return self.title

    @property
    def url(self):
        return '{}?_certificate={}'.format(reverse('certificate'), self.certificate_id)

    @property
    def title(self):
        return self.certificate.__unicode__()

    @property
    def count(self):
        return 1

    def get_vendor_code(self):
        return self.certificate.vendor_code

    def count_price(self):
        return self.certificate.price

    def save(self, *args, **kwargs):
        self.price = self.count_price()
        return super(CertificateCartItem, self).save(*args, **kwargs)

    @property
    def price_int(self):
        price = self.price
        return to_int_plus(price)
