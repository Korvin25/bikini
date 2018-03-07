# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.catalog.models import Certificate


class CertificateCartItemForm(forms.Form):
    certificate = forms.IntegerField(label=_('Сертификат'))
    recipient_name = forms.CharField(label=_('Имя получателя'), max_length=255)
    recipient_email = forms.EmailField(label=_('Email получателя'), required=False)
    sender_name = forms.CharField(label=_('Имя отправителя'), max_length=255, required=False)
    sender_phone = forms.CharField(label=_('Телефон отправителя'), max_length=127)
    sender_email = forms.EmailField(label=_('Email отправителя'))
    message = forms.CharField(label=_('Сообщение получателю'), required=False)
    date = forms.CharField(label=_('Когда отправлять'), required=False)
    send_date = forms.DateField(label=_('Дата отправки'), required=False)

    def clean_certificate(self):
        certificate_id = self.cleaned_data.get('certificate')
        if not Certificate.objects.filter(id=certificate_id).exists():
            raise forms.ValidationError(_('Сертификата с таким ID не существует.'))
        return certificate_id

    def clean_send_date(self):
        """
        date in ['today', 'on_date']
        """
        send_date = self.cleaned_data.get('send_date')
        date = self.cleaned_data.get('date')
        if date != 'on_date':
            send_date = None
        elif not send_date:
            raise forms.ValidationError(_('Обязательное поле.'))
        return send_date
