# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import Setting, VisualSetting, SEOSetting


def settings(request):
    if request.path.startswith('/admin/'):
        return {}

    settings = {key: value for key, value in Setting.objects.values_list('key', 'value')}
    visual_settings = {key: value for key, value in VisualSetting.objects.values_list('key', 'value')}
    settings.update(visual_settings)
    seo_settings = {setting.key: setting for setting in SEOSetting.objects.all()}

    return {
        'settings': settings,
        'seo_settings': seo_settings,
    }
