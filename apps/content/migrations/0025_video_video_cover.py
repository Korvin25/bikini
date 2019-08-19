# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0024_another_three_regions'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='video_cover',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='videos/yt/covers/', verbose_name='\u041e\u0431\u043b\u043e\u0436\u043a\u0430 \u0441 YouTube'),
        ),
    ]
