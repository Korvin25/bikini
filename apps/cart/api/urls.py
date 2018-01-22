# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import (Step0View, Step2View, Step3View,
                    UpdateCartView, CartAjaxView,)


urlpatterns = [
    url(r'^steps/0/$', Step0View.as_view(), name='step0'),
    url(r'^steps/2/$', Step2View.as_view(), name='step2'),
    url(r'^steps/3/$', Step3View.as_view(), name='step3'),

    url(r'^update/$', UpdateCartView.as_view(), name='update'),

    url(r'^set/$', CartAjaxView.as_view(action='set'), name='set'),
    url(r'^remove/$', CartAjaxView.as_view(action='remove'), name='remove'),
    url(r'^clear/$', CartAjaxView.as_view(action='clear'), name='clear'),
]
