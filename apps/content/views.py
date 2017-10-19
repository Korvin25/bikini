# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView

from ..catalog.models import Product
from .models import HomepageSlider


class HomepageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        slide = HomepageSlider.objects.first()
        products = Product.objects.filter(product_type='default',
                                          show=True, show_at_homepage=True).order_by('order_at_homepage', '-id')
        context = {
            'slide': slide,
            'products': products,
        }
        context.update(super(HomepageView, self).get_context_data(**kwargs))
        return context
