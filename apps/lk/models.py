# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.core.urlresolvers import reverse
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

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
    email = models.EmailField('Email', unique=True)
    date_joined = models.DateTimeField('Дата и время регистрации', auto_now_add=True)
    subscription = models.BooleanField('Подписан на рассылку', default=True)

    is_active = models.BooleanField('Активен?', default=True)
    is_staff = models.BooleanField('Имеет доступ к админ-панели', default=False)

    # --- данные для доставки ---
    country = models.ForeignKey(Country, verbose_name='Страна', null=True, blank=True)
    city = models.CharField('Город', max_length=225, null=True, blank=True)
    address = models.TextField('Адрес', null=True, blank=True)
    phone = models.CharField('Телефон', max_length=30, null=True, blank=True)
    name = models.CharField('Полное имя', max_length=511, null=True, blank=True)

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

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __unicode__(self):
        return '{} ({})'.format(self.name, self.email) if self.name else self.email

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
            'city': self.city,
            'address': self.address,
            'phone': self.phone,
            'name': self.name,
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
        return list(self.wishlist_items.all().values('product_id', 'price', 'attrs'))


class WishListItem(models.Model):
    profile = models.ForeignKey(Profile, verbose_name='Профиль', related_name='wishlist_items')
    product = models.ForeignKey('catalog.Product', verbose_name='Товар', related_name='wishlist_items')
    price = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)
    attrs = JSONField(default=dict)

    class Meta:
        unique_together = ('profile', 'product')
        ordering = ['id', ]

    def __unicode__(self):
        return self.id
