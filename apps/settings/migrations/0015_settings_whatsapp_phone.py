# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0014_another_three_regions'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='whatsapp_phone',
            field=models.CharField(default='+7 902 354-38-45', max_length=127, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0432 Whatsapp'),
        ),
    ]
