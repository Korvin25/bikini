# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import CertificateCartSetView, CertificateCartRemoveView


urlpatterns = [
    url(r'^set/$', CertificateCartSetView.as_view(), name='set'),
    url(r'^remove/$', CertificateCartRemoveView.as_view(), name='remove'),
]
