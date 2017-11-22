# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView

from ..catalog.models import Product
from ..banners.models import PromoBanner


class HomepageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        banner = PromoBanner.objects.prefetch_related('girls').filter(is_enabled=True).order_by('?').first()
        if not banner:
            banner = PromoBanner.objects.prefetch_related('girls').all().order_by('?').first()
        products = Product.objects.select_related('category').filter(show=True,
                                                                     show_at_homepage=True).order_by('order_at_homepage', '-id')
        context = {
            'promo_banner': banner,
            'products': products,
        }
        context.update(super(HomepageView, self).get_context_data(**kwargs))
        return context
