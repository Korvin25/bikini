# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
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

    country = models.ForeignKey(Country, verbose_name='Страна', null=True, blank=True)
    city = models.CharField('Город', max_length=225, null=True, blank=True)
    address = models.TextField('Адрес', null=True, blank=True)
    phone = models.CharField('Телефон', max_length=30, null=True, blank=True)
    name = models.CharField('Полное имя', max_length=511, null=True, blank=True)

    desired_products = models.ManyToManyField('catalog.Product', verbose_name='Желаемые товары', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def get_short_name(self):
        return self.email

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
