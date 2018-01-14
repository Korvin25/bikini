# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import PostListView, PostDetailView


urlpatterns = [
    url(r'^$', PostListView.as_view(with_category=False), name='home'),
    url(r'^(?P<slug>[^/]+)/$', PostListView.as_view(with_category=True), name='category'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[^/]+)-(?P<pk>\d+)/$', PostDetailView.as_view(), name='post'),
]
