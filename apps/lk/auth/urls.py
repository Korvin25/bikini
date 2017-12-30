# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include

from .views import LoginView, LogoutView, RegistrationView


urlpatterns = [
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^registration/$', RegistrationView.as_view(), name='registration'),
    # url(r'^reset_password/$', ResetPasswordView.as_view(), name='reset_password'),
]
