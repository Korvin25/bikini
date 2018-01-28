# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import WishListView, WishListAddView, WishListRemoveView


urlpatterns = [
    url(r'^$', WishListView.as_view(), name='home'),
    url(r'^add/$', WishListAddView.as_view(), name='add'),
    url(r'^remove/$', WishListRemoveView.as_view(), name='remove'),
]
