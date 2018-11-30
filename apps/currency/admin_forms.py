# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib import messages
# from django.utils import timezone

from crequest.middleware import CrequestMiddleware

from .models import EUR, USD
from .tasks import update_prices


class CurrencyAdminForm(forms.ModelForm):
    model = None

    # def clean_rate(self):
    #     rate = self.cleaned_data.get('rate')
    #     rate_obj = self.model.get_solo()
    #     now = timezone.now()

    #     if (now - rate_obj.update_dt).hours < 1:
    #         raise forms.ValidationError('Вы уже изменяли курс в этом часу.')

    #     return rate

    def save(self, commit=True):
        currency = super(CurrencyAdminForm, self).save(commit=False)
        currency_name = self.model.__name__.lower()

        result = update_prices.delay(currency_name, currency.rate)
        currency.celery_task_id = result.id
        currency.save()

        request = CrequestMiddleware.get_request()
        message = 'Запущен процесс изменения цен на сайте. Это может занять до нескольких минут.'
        messages.warning(request, message)
        return currency



class EURAdminForm(CurrencyAdminForm):
    model = EUR

    class Meta:
        model = EUR
        fields = '__all__'


class USDAdminForm(CurrencyAdminForm):
    model = USD

    class Meta:
        model = USD
        fields = '__all__'
