# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0029_add_cart_clean_cost_and_delivery_cost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentmethod',
            name='is_paypal',
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='payment_type',
            field=models.CharField(choices=[('yookassa', 'YooKassa'), ('paypal', 'PayPal'), ('offline', '\u043d\u0430\u043b\u0438\u0447\u043d\u044b\u0435')], default='offline', max_length=15, verbose_name='\u0422\u0438\u043f \u043e\u043f\u043b\u0430\u0442\u044b'),
        ),
    ]
