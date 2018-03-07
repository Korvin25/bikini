# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import JsonResponse, HttpResponse
from django.http.request import QueryDict
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __

from .utils import get_error_message


translated_strings = (_('Неправильный формат запроса'), _('Ошибка при парсинге запроса'),)


class GetNotAllowedMixin(object):
    """
    Для предотвращения ошибок вида
    "ImproperlyConfigured: TemplateResponseMixin requires either a definition of 'template_name'"
    во вьюхах с формами (CreateView, etc)
    """

    def get(self, request, *args, **kwargs):
        return HttpResponse(status=405)


class JSONViewMixin(GetNotAllowedMixin):

    def dispatch(self, request, *args, **kwargs):
        self.DATA = {}

        if self.request.method == 'POST':
            try:
                self.DATA = json.loads(request.body.decode('utf-8'))
            except Exception as e:
                err_message = get_error_message(e)
                data = {'result': 'error', 'error': __('Неправильный формат запроса')}
                return JsonResponse(data, status=400)

        return super(JSONViewMixin, self).dispatch(request, *args, **kwargs)
        


class JSONFormMixin(GetNotAllowedMixin):
    mapping = {}

    def dispatch(self, request, *args, **kwargs):
        self.errors = []
        self.reverse_mapping = self.get_reverse_mapping()

        if self.request.method == 'POST':
            self.JSON_POST = {}
            try:
                self.JSON_POST = json.loads(request.body.decode('utf-8'))
            except Exception as e:
                err_message = get_error_message(e)
                message_label = __('Ошибка при парсинге запроса')
                error = {'name': '__all__', 'error_message': '{}: {}'.format(message_label, err_message)}
                data = {'errors': [error]}
                return JsonResponse(data, status=400)

            self.POST = self.get_post_data()

        return super(JSONFormMixin, self).dispatch(request, *args, **kwargs)

    def get_reverse_mapping(self):
        return {value: key for key, value in self.mapping.iteritems()}

    def get_post_data(self):
        POST = QueryDict(mutable=True)
        for key, value in self.JSON_POST.iteritems():
            post_key = self.mapping.get(key)
            if post_key:
                POST.update({post_key: value})
        return POST

    def get_form(self, *args, **kwargs):
        if hasattr(self, 'get_object'):
            form = self.form_class(self.POST, instance=self.get_object())
        else:
            form = self.form_class(self.POST)
        return form

    def form_invalid(self, form):
        errors = []
        for k in form.errors:
            if k == '__all__':
                errors.append({'name': k, 'error_message': form.errors[k][0]})
            else:
                errors.append({'name': k, 'label': form[k].label, 'error_message': form.errors[k][0]})
        return JsonResponse({'errors': errors}, status=400)
