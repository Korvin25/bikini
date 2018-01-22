# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import ContestsHomeView, ContestDetailView, ParticipantDetailView, ApplyView, AddLikeView, RemoveLikeView


urlpatterns = [
    url(r'^$', ContestsHomeView.as_view(), name='home'),
    url(r'^(?P<slug>[^/]+)/$', ContestDetailView.as_view(), name='contest'),
    url(r'^(?P<contest_slug>[^/]+)/participants/(?P<pk>\d+)/$', ParticipantDetailView.as_view(), name='participant'),
    url(r'^participants/apply/$', ApplyView.as_view(), name='apply'),
    url(r'^participants/like/$', AddLikeView.as_view(), name='like'),
    url(r'^participants/dislike/$', RemoveLikeView.as_view(), name='dislike'),
]
