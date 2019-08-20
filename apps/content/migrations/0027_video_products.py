# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_video_products(apps, schema_editor):
    Video = apps.get_model('content', 'Video')

    for obj in Video.objects.filter(product__gt=0):
        obj.products.add(obj.product)


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0026_video_products'),
    ]

    operations = [
        migrations.RunPython(set_video_products, reverse_code=migrations.RunPython.noop),
    ]
