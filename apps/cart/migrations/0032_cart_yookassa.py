# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0031_cart_yookassa'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cart',
            old_name='yoo_return_url',
            new_name='yoo_redirect_url',
        ),
    ]
