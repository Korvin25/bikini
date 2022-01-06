# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from md5 import md5

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View

from rauth.compat import urlencode
from rauth.service import OAuth2Service, OAuth1Service
from rauth.utils import parse_utf8_qsl
import requests

from apps.lk.models import Profile


class BaseSocialView(View):
    network = ''
    _facebook = OAuth2Service(
        name=str('facebook'),
        authorize_url=settings.FACEBOOK_AUTHORIZE_URL,
        access_token_url=settings.FACEBOOK_BASE_URL + 'oauth/access_token',
        client_id=settings.FACEBOOK_CONSUMER_KEY,
        client_secret=settings.FACEBOOK_CONSUMER_SECRET,
        base_url=settings.FACEBOOK_BASE_URL,
    )
    _vk = OAuth2Service(
        name=str('vk'),
        authorize_url=settings.VKONTAKTE_AUTHORIZE_URL,
        access_token_url=settings.VKONTAKTE_BASE_URL + 'access_token',
        client_id=settings.VKONTAKTE_CONSUMER_KEY,
        client_secret=settings.VKONTAKTE_CONSUMER_SECRET,
        base_url=settings.VKONTAKTE_BASE_URL,
    )
    _gplus = OAuth2Service(
        name=str('gp'),
        authorize_url=settings.GOOGLE_PLUS_AUTHORIZE_URL,
        access_token_url=settings.GOOGLE_PLUS_ACCESS_TOKEN_URL,
        client_id=settings.GOOGLE_PLUS_CONSUMER_KEY,
        client_secret=settings.GOOGLE_PLUS_CONSUMER_SECRET,
        base_url=settings.GOOGLE_PLUS_BASE_URL,
    )
    _instagram = OAuth2Service(
        name=str('instagram'),
        authorize_url=settings.INSTAGRAM_AUTHORIZE_URL,
        access_token_url=settings.INSTAGRAM_ACCESS_TOKEN_URL,
        client_id=settings.INSTAGRAM_CONSUMER_KEY,
        client_secret=settings.INSTAGRAM_CONSUMER_SECRET,
        base_url=settings.INSTAGRAM_BASE_URL,
    )
    services = {
        'fb': lambda self, **params: self._facebook.get_authorize_url(scope='email', **params),
        'vk': lambda self, **params: self._vk.get_authorize_url(scope='email', **params),
        'gp': lambda self, **params: self._gplus.get_authorize_url(**params),
        'ig': lambda self, **params: self._instagram.get_authorize_url(**params),
    }

    def get_authorize_url(self):
        self.url = self.request.build_absolute_uri().split("?")[0]

        params = {'redirect_uri': self.url}
        if self.network == 'gp':
            params.update({
                'access_type': 'offline',
                # 'include_granted_scopes': 'true',
                'response_type': 'code',
                # 'scope': 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
                'scope': 'https://www.googleapis.com/auth/userinfo.email',
            })
        if self.network == 'ig':
            params.update({
                'response_type': 'code',
            })
        authorize_url = self.services[self.network](self, **params)
        return authorize_url

    def get_user_data(self):
        self.url = self.request.build_absolute_uri().split("?")[0]
        user_data = {}
        data = {'code': self.request.GET.get('code'), 'redirect_uri': self.url}

        if self.network == 'gp':
            data.update({'grant_type': 'authorization_code'})
        if self.network == 'ig':
            data.update({'grant_type': 'authorization_code'})
        user_data = getattr(self, 'get_{}_data'.format(self.network))(data)

        if not user_data.get('name') and user_data.get('first_name') and user_data.get('last_name'):
            user_data['name'] = ' '.join([user_data['first_name'], user_data['last_name']])

        params = {'{}_id'.format(self.network): user_data['uid']}
        profile = Profile.objects.filter(**params).first()

        if profile:
            user_data['profile'] = profile
        elif Profile.objects.filter(email=user_data.get('email')).count():
            user_data['email'] = None
        return user_data

    def get_fb_data(self, data):
        try:
            # --old--
            # session = self._facebook.get_auth_session(data=data)

            # --new--
            response = self._facebook.get_raw_access_token(data=data)
            response = response.json()
            if response.get('error'):
                raise Exception(response['error'].get('message') or 'Unknown error')
            token = response.get('access_token')
            session = self._facebook.get_session(token=token)

            # ----
            response = session.get('me', params={'fields': 'id,email,name,first_name,last_name,picture,cover,link'})
            response = response.json()

            id = str(response.get('id'))
            email = response.get('email', '')
            name = response.get('name', '')
            first_name = response.get('first_name', '')
            last_name = response.get('last_name', '')
            link = response.get('link', '')
            photo = ''
            if (response.get('picture')
                and response['picture'].get('data')):
                photo = response['picture']['data'].get('url')
            cover = ''
            if response.get('cover'):
                cover = response['cover'].get('source')

        except Exception as e:
            err_message = str(e.message).decode('utf-8') or str(e).decode('utf-8')
            raise Exception('Error while getting data from Facebook: {}'.format(err_message))
        else:
            return {
                'uid': id,
                'email': email,
                'name': name,
                'first_name': first_name,
                'last_name': last_name,
                'photo': photo,
                'cover': cover,
                'link': link,
            }

    def _vk_method(self, method_name, params, token):
        api_url = settings.VKONTAKTE_API_URL
        url = '{}/{}'.format(api_url, method_name)
        params.update({'access_token': token, 'v': '5.131'})
        response = requests.get(url, params)
        return response

    def get_vk_data(self, data):
        try:
            response = self._vk.get_raw_access_token(data=data)
            response = response.json()
            if response.get('error'):
                raise Exception(response.get('error_description') or 'Unknown error')

            id = str(response.get('user_id'))
            email = response.get('email', '')
            token = response.get('access_token')

            self._vk.get_session(token=token)
            response = self._vk_method('users.get', params={'user_ids': id, 'fields': 'photo_200,screen_name'}, token=token)
            response = response.json()
            user = response['response'][0]

            first_name = user.get('first_name', '')
            last_name = user.get('last_name', '')
            name = ' '.join([first_name, last_name])
            photo = user.get('photo_max', '')
            photo = photo or user.get('photo_200', '')
            link = user.get('screen_name', '')

        except Exception as e:
            err_message = str(e.message).decode('utf-8') or str(e).decode('utf-8')
            raise Exception('Error while getting data from VK: {}'.format(err_message))
        else:
            return {
                'uid': id,
                'email': email,
                'name': name,
                'first_name': first_name,
                'last_name': last_name,
                'photo': photo,
                'link': link,
            }

    def _gp_method(self, method_name, params, token):
        api_url = settings.GOOGLE_PLUS_API_URL
        url = '{}/{}'.format(api_url, method_name)
        params.update({'access_token': token})
        response = requests.get(url, params)
        return response

    def get_gp_data(self, data):
        try:
            response = self._gplus.get_raw_access_token(data=data)
            response = response.json()
            if response.get('error'):
                raise Exception(response.get('error_description') or 'Unknown error')

            token = response.get('access_token')

            response = self._gp_method('people/me', params={}, token=token)
            response = response.json()

            if response.get('error'):
                raise Exception(response['error'].get('message') or 'Unknown error')

            id = response['id']
            link = response.get('url')

            email = ''
            emails = response.get('emails')
            if emails and emails[0]:
                email = emails[0].get('value', '')

            name = response.get('displayName')
            first_name = last_name = ''
            if response.get('name'):
                first_name = response['name'].get('givenName', '')
                last_name = response['name'].get('familyName', '')

            photo = ''
            if response.get('image'):
                photo = response['image'].get('url')

            cover = ''
            if response.get('cover') and response['cover'].get('coverPhoto'):
                cover = response['cover']['coverPhoto'].get('url')

        except Exception as e:
            err_message = str(e.message).decode('utf-8') or str(e).decode('utf-8')
            raise Exception('Error while getting data from Google+: {}'.format(err_message))

        else:
            return {
                'uid': id,
                'link': link,
                'email': email,
                'name': name,
                'first_name': first_name,
                'last_name': last_name,
                'photo': photo,
                'cover': cover,
            }

    def get_ig_data(self, data):
        try:
            response = self._instagram.get_raw_access_token(data=data)
            response = response.json()
            if response.get('error'):
                raise Exception(response.get('error_description') or 'Unknown error')

            token = response.get('access_token')
            user = response.get('user', {})
            if user:
                id = user.get('id')
                link = user.get('username')
                photo = user.get('profile_picture')
                name = user.get('full_name')
            else:
                raise Exception('No "user" object in response')

        except Exception as e:
            err_message = str(e.message).decode('utf-8') or str(e).decode('utf-8')
            raise ErrorWithCode(detail='Error while getting data from Instagram: {}'.format(err_message),
                                code='IG_OAUTH_ERROR')

        else:
            return {
                'uid': id,
                'name': name,
                'photo': photo,
                'link': link,
            }
