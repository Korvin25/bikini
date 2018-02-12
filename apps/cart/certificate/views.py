# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import TemplateView

from apps.catalog.models import Certificate
from apps.cart.models import DeliveryMethod, PaymentMethod


class CertificateView(TemplateView):
    template_name = 'cart/certificate.html'

    def get_certificate(self):
        certificates = Certificate.objects.all()
        certificate = certificates.first()

        cert_id = self.request.GET.get('_certificate', 0)
        if cert_id:
            try:
                certificate = certificates.get(id=cert_id)
            except (ValueError, Certificate.DoesNotExist):
                pass

        self.certificates = certificates
        self.certificate = certificate

    def get_context_data(self, **kwargs):
        self.get_certificate()
        context = {
            'certificates': self.certificates,
            'certificate': self.certificate,
            'delivery_methods': DeliveryMethod.objects.filter(is_enabled=True),
            'payment_methods': PaymentMethod.objects.filter(is_enabled=True),
        }
        context.update(super(CertificateView, self).get_context_data(**kwargs))
        return context
