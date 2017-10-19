# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from ..geo.models import Country, City


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
    name = models.CharField('ФИО', max_length=511, blank=True)
    date_joined = models.DateTimeField('Дата и время регистрации', auto_now_add=True)
    subscription = models.BooleanField('Подписан на рассылку', default=True)

    is_active = models.BooleanField('Активен?', default=True)
    is_staff = models.BooleanField('Имеет доступ к админ-панели', default=False)

    country = models.ForeignKey(Country, verbose_name='Страна', null=True, blank=True)
    city = models.ForeignKey(City, verbose_name='Город', null=True, blank=True)
    index = models.CharField('Индекс', max_length=15, null=True, blank=True)
    street = models.CharField('Улица', max_length=63, null=True, blank=True)
    house = models.CharField('Дом', max_length=7, null=True, blank=True)
    building = models.CharField('Строение', max_length=7, null=True, blank=True)
    housing = models.CharField('Корпус', max_length=7, null=True, blank=True)
    flat = models.CharField('Квартира', max_length=7, null=True, blank=True)
    phone = models.CharField('Контактный телефон', max_length=31, null=True, blank=True)

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
