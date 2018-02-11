# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import CallbackOrderFormView


urlpatterns = [
    url(r'^callback/$', CallbackOrderFormView.as_view(), name='callback'),
]
