# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import get_object_or_404


def get_object_from_slug_and_kwargs(request, model, slug, **kwargs):
    object = None
    try:
        object = get_object_or_404(model, slug=slug, **kwargs)
    except Http404 as exc:
        if request.LANGUAGE_CODE != 'ru':
            try:
                object = get_object_or_404(model, slug_en=slug, **kwargs)
            except Http404:
                object = get_object_or_404(model, slug_ru=slug, **kwargs)
        else:
            raise exc
    return object
