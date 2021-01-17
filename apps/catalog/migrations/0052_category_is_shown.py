# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0051_load_product_tabs'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_shown',
            field=models.BooleanField(default=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043d\u0430 \u0441\u0430\u0439\u0442\u0435'),
        ),
    ]
