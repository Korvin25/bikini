# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.generic import CreateView

from ..core.mixins import JSONFormMixin
# from ..lk.email import admin_send_order_email, send_order_email
from .forms import CallbackOrderForm
from .models import CallbackOrder


class CallbackOrderFormView(JSONFormMixin, CreateView):
    form_class = CallbackOrderForm
    model = CallbackOrder
    mapping = {
        'name': 'name',
        'phone': 'phone',
    }

    def get_success_url(self):
        return self.request.path

    def get_object(self):
        return None

    def form_valid(self, form):
        super(CallbackOrderFormView, self).form_valid(form)
        order = form.instance

        profile = self.request.user
        if profile.is_authenticated():
            order.profile = profile
            order.save()

        # send_admin_order_email(order=cart)
        # send_customer_order_email(order.profile, order=cart)

        success_message = 'Спасибо! Мы обязательно вам перезвоним.'
        data = {'result': 'ok', 'order_id': order.id, 'success_message': success_message}
        return JsonResponse(data)
