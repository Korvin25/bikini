# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from .views import SocialLoginView


urlpatterns = [
    url(r'^login/fb/$', SocialLoginView.as_view(network='fb'), name='fb'),
    url(r'^login/vk/$', SocialLoginView.as_view(network='vk'), name='vk'),
    url(r'^login/gp/$', SocialLoginView.as_view(network='gp'), name='gp'),
    url(r'^login/ig/$', SocialLoginView.as_view(network='ig'), name='ig'),
]
