# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View

from .utils import set_currency


class SetCurrencyView(View):

    def post(self, request, *args, **kwargs):
        currency = request.POST.get('currency')
        next = request.POST.get('next', reverse('home'))

        set_currency(request, currency)
        return HttpResponseRedirect(next)
