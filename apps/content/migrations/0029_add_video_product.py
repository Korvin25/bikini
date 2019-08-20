# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0048_another_three_regions'),
        ('content', '0028_remove_video_product'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='video',
        #     name='product',
        #     field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='catalog.Product', verbose_name='\u0422\u043e\u0432\u0430\u0440'),
        # ),
    ]
