# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0035_update_cart_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='payment_type_cost_eur',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='\u041d\u0430\u0446\u0435\u043d\u043a\u0430 \u0437\u0430 \u0442\u0438\u043f \u043e\u043f\u043b\u0430\u0442\u044b, eur.'),
        ),
        migrations.AddField(
            model_name='cart',
            name='payment_type_cost_percent',
            field=models.FloatField(default=0, verbose_name='\u041d\u0430\u0446\u0435\u043d\u043a\u0430 \u0437\u0430 \u0442\u0438\u043f \u043e\u043f\u043b\u0430\u0442\u044b, %'),
        ),
        migrations.AddField(
            model_name='cart',
            name='payment_type_cost_rub',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='\u041d\u0430\u0446\u0435\u043d\u043a\u0430 \u0437\u0430 \u0442\u0438\u043f \u043e\u043f\u043b\u0430\u0442\u044b, rub.'),
        ),
        migrations.AddField(
            model_name='cart',
            name='payment_type_cost_usd',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='\u041d\u0430\u0446\u0435\u043d\u043a\u0430 \u0437\u0430 \u0442\u0438\u043f \u043e\u043f\u043b\u0430\u0442\u044b, usd.'),
        ),
        migrations.AddField(
            model_name='cart',
            name='paypal_id',
            field=models.UUIDField(blank=True, null=True, verbose_name='PayPal: ID \u043f\u043b\u0430\u0442\u0435\u0436\u0430'),
        ),
        migrations.AddField(
            model_name='cart',
            name='paypal_paid',
            field=models.NullBooleanField(default=None, verbose_name='PayPal: \u041e\u043f\u043b\u0430\u0447\u0435\u043d?'),
        ),
        migrations.AddField(
            model_name='cart',
            name='paypal_popup_showed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cart',
            name='paypal_redirect_url',
            field=models.URLField(blank=True, null=True, verbose_name='PayPal: URL \u0434\u043b\u044f \u043f\u0435\u0440\u0435\u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f'),
        ),
        migrations.AddField(
            model_name='cart',
            name='paypal_status',
            field=models.CharField(blank=True, choices=[('pending', '\u043d\u0435 \u043e\u043f\u043b\u0430\u0447\u0435\u043d'), ('succeeded', '\u043e\u043f\u043b\u0430\u0447\u0435\u043d'), ('canceled', '\u043e\u0442\u043c\u0435\u043d\u0435\u043d'), ('error', '\u043e\u0448\u0438\u0431\u043a\u0430')], default='', max_length=15, null=True, verbose_name='PayPal: \u0421\u0442\u0430\u0442\u0443\u0441 \u043f\u043b\u0430\u0442\u0435\u0436\u0430'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, '\u043d\u043e\u0432\u044b\u0439'), (1, '\u043f\u0440\u0438\u043d\u044f\u0442'), (2, '\u043e\u0442\u043f\u0440\u0430\u0432\u043b\u0435\u043d'), (3, '\u0438\u0441\u043f\u043e\u043b\u043d\u0435\u043d'), (4, '\u043e\u0442\u043c\u0435\u043d\u0435\u043d')], default=0, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441 \u0434\u043e\u0441\u0442\u0430\u0432\u043a\u0438'),
        ),
    ]
