# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.widgets import ImageClearableFileInput


class ImageThumbAdminMixin(object):
    formfield_overrides = {
        models.ImageField: {'widget': ImageClearableFileInput},
        ThumbnailerImageField: {'widget': ImageClearableFileInput},
    }
