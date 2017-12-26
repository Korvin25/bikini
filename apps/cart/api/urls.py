# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import CartAjaxView


urlpatterns = [
    url(r'^set/$', CartAjaxView.as_view(action='set'), name='set'),
    url(r'^remove/$', CartAjaxView.as_view(action='remove'), name='remove'),
    url(r'^clear/$', CartAjaxView.as_view(action='clear'), name='clear'),
]
