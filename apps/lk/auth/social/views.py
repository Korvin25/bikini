# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urlparse
import uuid

from django.contrib.auth import authenticate, login, logout
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

import requests

from apps.cart.cart import Cart
# from apps.lk.email import admin_send_registration_email, send_registration_email
from apps.lk.models import Profile
from apps.lk.auth.utils import update_wishlist
from .base import BaseSocialView


class SocialLoginView(BaseSocialView):

    def _get_random_str(self):
        return uuid.uuid4().hex[:6]

    def _get_email_placeholder(self, id=''):
        if not id:
            id = self._get_random_str()
        return '{}+{}@bikinimini.ru'.format(self.network, id)

    # def _save_image_from_url(self, field, url):
    #     r = requests.get(url)
    #     if r.status_code == requests.codes.ok:
    #         try:
    #             img_temp = NamedTemporaryFile()
    #             img_temp.write(r.content)
    #             img_temp.flush()
    #             img_filename = urlparse.urlsplit(url).path[1:]
    #             if not img_filename.count('.'):
    #                 img_filename = '{}.jpg'.format(img_filename)
    #             field.save(img_filename, File(img_temp), save=True)
    #             return True
    #         except Exception as e:
    #             pass
    #     return False

    def get(self, request, *args, **kwargs):
        if request.GET.get('code') or request.GET.get('oauth_verifier'):
            # получаем данные из соц.сетки
            user_data = self.get_user_data()
            redirect_url = reverse('profile')

            if user_data.get('profile'):
                # если чувак есть на сайте, логиним его
                profile = user_data['profile']
                profile.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, profile)
                # redirect_url = profile.get_after_login_url()

                # переносим текущую корзину и вишлист
                cart = Cart(request).cart
                cart.profile = profile
                cart.save()
                update_wishlist(request, profile)

            else:
                # иначе регаем:

                # получаем мыло
                email = user_data.get('email')
                has_email = True

                if not email:
                    email = self._get_email_placeholder()
                    has_email = False

                # создаем чела
                profile = Profile.objects.create(email=email, has_email=has_email)
                profile.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, profile)

                # переносим текущую корзину и вишлист
                cart = Cart(request).cart
                cart.profile = profile
                cart.save()
                update_wishlist(request, profile)

                # заполняем поля социалки
                setattr(profile, '{}_id'.format(self.network), user_data.get('uid'))
                setattr(profile, '{}_name'.format(self.network), user_data.get('name'))
                setattr(profile, '{}_link'.format(self.network), user_data.get('link'))

                # и имя
                first_name = user_data.get('first_name', '')
                last_name = user_data.get('last_name', '')
                if first_name or last_name:
                    profile.name = ' '.join([first_name, last_name]).strip()
                else:
                    profile.name = user_data.get('name', '')
                profile.save()

                # # и фотки
                # if user_data.get('photo'):
                #     self._save_image_from_url(profile.avatar, user_data['photo'])
                # if user_data.get('cover'):
                #     self._save_image_from_url(profile.cover, user_data['cover'])

                # # отправляем письма о реге
                # if has_email:
                #     profile.get_signature()
                #     send_registration_email(profile)
                #     admin_send_registration_email(profile)
                # # else:
                # #     profile.email = self._get_email_placeholder(profile.id)
                # #     profile.save(check_if_filed=False)

                # # редирект
                # if has_email:
                #     redirect_url = '{}?p=first_visit'.format(reverse('profile:edit'))
            return HttpResponseRedirect(redirect_url)

        # получаем код из соц.сетки
        authorize_url = self.get_authorize_url()
        return HttpResponseRedirect(authorize_url)
