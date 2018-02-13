# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView, View

from apps.catalog.models import Certificate
from apps.cart.cart import Cart
from apps.cart.models import DeliveryMethod, PaymentMethod
from apps.core.mixins import JSONFormMixin, JSONViewMixin
from .forms import CertificateCartItemForm


class CertificateCartSetView(JSONFormMixin, FormView):
    form_class = CertificateCartItemForm
    # template_name = 'cart/certificate.html'
    mapping = {
        'certificate': 'certificate',
        'recipient_name': 'recipient_name',
        'recipient_email': 'recipient_email',
        'sender_name': 'sender_name',
        'sender_phone': 'sender_phone',
        'sender_email': 'sender_email',
        'message': 'message',
        'date': 'date',
        'send_date': 'send_date',
    }

    def get_success_url(self, *args, **kwargs):
        return reverse('certificate')

    def form_valid(self, form):
        cart = Cart(self.request)
        cleaned_data = form.cleaned_data

        certificate_id = cleaned_data.get('certificate')
        kwargs = {}
        kwargs['send_immediately'] = not (cleaned_data.get('date') == 'on_date')
        for slug in ['recipient_name', 'recipient_email', 'sender_name', 'sender_phone',
                     'sender_email', 'message', 'send_date']:
            kwargs[slug] = cleaned_data.get(slug)

        item = cart.set_certificate(certificate_id, **kwargs)
        count = cart.count()
        summary = cart.summary()

        data = {'result': 'ok', 'count': count, 'summary': summary}
        return JsonResponse(data)


class CertificateCartRemoveView(JSONViewMixin, View):

    def post(self, request, *args, **kwargs):
        cart = Cart(request)

        print self.DATA
        cart.remove_certificate(item_id=self.DATA.get('item_id', 0))
        count = cart.count()
        summary = cart.summary()

        data = {'result': 'ok', 'count': count, 'summary': summary}
        return JsonResponse(data)


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
