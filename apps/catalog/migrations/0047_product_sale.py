# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0046_product_sale'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='is_on_sale',
            field=models.BooleanField(default=False, verbose_name='\u0415\u0441\u0442\u044c \u0441\u043a\u0438\u0434\u043a\u0430?'),
        ),
    ]
