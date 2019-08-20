# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0048_another_three_regions'),
        ('content', '0025_video_video_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='products',
            field=models.ManyToManyField(blank=True, related_name='video_set', to='catalog.Product', verbose_name='\u0422\u043e\u0432\u0430\u0440\u044b'),
        ),
    ]
