# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
import uuid

from django.core.urlresolvers import reverse
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ..cart.utils import make_hash_from_cartitem
from ..currency.utils import price_with_currency
from ..geo.models import Country


class UserManager(BaseUserManager):

    def create_user(self, email, password):

        if not email:
            raise ValueError('Email: required fiield')

        if not password:
            raise ValueError('Password: required field')

        user = self.model(
            email=UserManager.normalize_email(email),
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
        )

        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user

    def get_by_natural_key(self, username):
        """
        Делаем логин регистронезависимым.

        https://djangosnippets.org/snippets/1368/
        (comment by bquinn at February 12, 2014)
        """
        return self.get(email__iexact=username)


class Profile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email'), unique=True)
    date_joined = models.DateTimeField('Дата и время регистрации', auto_now_add=True)
    subscription = models.BooleanField('Подписан на рассылку', default=True)

    is_active = models.BooleanField('Активен?', default=True, help_text='снимите галку, чтобы заблокировать юзера')
    is_staff = models.BooleanField('Имеет доступ к админ-панели', default=False)

    # --- данные из формы в профиле ---
    country = models.ForeignKey(Country, verbose_name=_('Страна'), null=True, blank=True)
    city = models.CharField(_('Город'), max_length=225, null=True, blank=True)
    address = models.TextField(_('Адрес'), null=True, blank=True)
    phone = models.CharField(_('Телефон'), max_length=30, null=True, blank=True)
    name = models.CharField(_('Полное имя'), max_length=511, null=True, blank=True)

    delivery_method = models.ForeignKey('cart.DeliveryMethod', verbose_name=_('Способ доставки'), null=True, blank=True)
    payment_method = models.ForeignKey('cart.PaymentMethod', verbose_name=_('Способ оплаты'), null=True, blank=True)

    # --- соц.сети ---
    fb_id = models.CharField('Facebook ID', max_length=255, null=True, blank=True)
    fb_name = models.CharField('Facebook name', max_length=255, null=True, blank=True)
    fb_link = models.CharField('Facebook link', max_length=255, null=True, blank=True)
    vk_id = models.CharField('VK ID', max_length=255, null=True, blank=True)
    vk_name = models.CharField('VK name', max_length=255, null=True, blank=True)
    vk_link = models.CharField('VK link', max_length=255, null=True, blank=True)
    gp_id = models.CharField('Google+ ID', max_length=255, null=True, blank=True)
    gp_name = models.CharField('Google+ name', max_length=255, null=True, blank=True)
    gp_link = models.CharField('Google+ link', max_length=255, null=True, blank=True)
    ig_id = models.CharField('Instagram ID', max_length=255, null=True, blank=True)
    ig_name = models.CharField('Instagram name', max_length=255, null=True, blank=True)
    ig_link = models.CharField('Instagram link', max_length=255, null=True, blank=True)

    # --- покупки со скидкой ---
    discount_code = models.CharField('Код скидки', max_length=127, null=True, blank=True)
    discount_used = models.BooleanField('Скидка использована?', default=False)

    has_email = models.BooleanField(default=True)
    has_password = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __unicode__(self):
        return ('{} ({}, id #{})'.format(self.name, self.email, self.id) if self.name and self.has_email
                else '{} (id #{})'.format(self.name, self.id) if self.name
                else '{} (id #{})'.format(self.email, self.id) if self.has_email
                else 'id #{}'.format(self.id))

    def get_short_name(self):
        return self.name or self.email

    def get_full_name(self):
        return self.__unicode__()

    @property
    def username(self):
        return self.email

    @property
    def shipping_data(self):
        data = {
            'country': self.country_id,
            'city': self.city or '',
            'address': self.address or '',
            'phone': self.phone or '',
            'name': self.name or '',
            'email': self.email if self.has_email else '',
            'payment_method_id': self.payment_method_id,
            'delivery_method_id': self.delivery_method_id,
        }
        data = {k: v for k, v in data.iteritems() if v}
        return data

    @property
    def complete_orders(self):
        return self.cart_set.filter(checked_out=True)

    @property
    def can_get_discount(self):
        from ..cart.models import CartItem
        complete_orders = self.complete_orders.values_list('id', flat=True)
        return (True if complete_orders.count() and not CartItem.had_discounts(cart_ids=complete_orders)
                                                and not self.discount_used
                else False)

    def get_discount_code(self):
        discount_code = self.discount_code
        if not discount_code:
            discount_code = self.discount_code = str(uuid.uuid4()).replace('-', '')
            self.save()
        return discount_code

    @property
    def wishlist(self):
        return list(self.wishlist_items.all().values('product_id', 'option_id', 'price_rub', 'price_eur', 'price_usd',
                                                     'attrs', 'extra_products', 'hash',))


class WishListItem(models.Model):
    profile = models.ForeignKey(Profile, verbose_name='Профиль', related_name='wishlist_items', db_index=True)
    product = models.ForeignKey('catalog.Product', verbose_name='Товар', related_name='wishlist_items', db_index=True)
    option = models.ForeignKey('catalog.ProductOption', verbose_name='Вариант', related_name='wishlist_items')

    attrs = JSONField(default=dict)
    extra_products = JSONField(default=dict)
    hash = models.BigIntegerField(default=0, db_index=True)

    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        ordering = ['id', ]

    def __unicode__(self):
        return '{}'.format(self.id)

    @property
    def price(self):
        return price_with_currency(self)

    def get_price(self):
        option = self.option
        option_price_rub = option.price_rub
        option_price_eur = option.price_eur
        option_price_usd = option.price_usd

        extra_price_rub = Decimal(0.0)
        extra_price_eur = Decimal(0.0)
        extra_price_usd = Decimal(0.0)
        if self.extra_products:
            extra_products = self.product.extra_products.filter(extra_product_id__in=self.extra_products.keys())
            prices = extra_products.values('price_rub', 'price_eur', 'price_usd')
            extra_price_rub = sum([price['price_rub'] for price in prices])
            extra_price_eur = sum([price['price_eur'] for price in prices])
            extra_price_usd = sum([price['price_usd'] for price in prices])

        self.price_rub = option_price_rub + extra_price_rub
        self.price_eur = option_price_eur + extra_price_eur
        self.price_usd = option_price_usd + extra_price_usd

    def save(self, *args, **kwargs):
        self.get_price()
        return super(WishListItem, self).save(*args, **kwargs)

    def set_hash(self):
        hash = make_hash_from_cartitem(self.attrs, self.extra_products)
        self.hash = hash
        self.save()
        return hash
