# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView


class CartView(TemplateView):
    template_name = 'cart/cart.html'
