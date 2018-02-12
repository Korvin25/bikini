# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView

from apps.catalog.models import Certificate
from apps.cart.models import DeliveryMethod, PaymentMethod, CertificateOrder


class CertificateView(TemplateView):
    template_name = 'cart/certificate.html'

    def get_context_data(self, **kwargs):
        context = {
            'certificates': Certificate.objects.filter(show=True),
            'delivery_methods': DeliveryMethod.objects.filter(is_enabled=True),
            'payment_methods': PaymentMethod.objects.filter(is_enabled=True),
        }
        context.update(super(CertificateView, self).get_context_data(**kwargs))
        return context
