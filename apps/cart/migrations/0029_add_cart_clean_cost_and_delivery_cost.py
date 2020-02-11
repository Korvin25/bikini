# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0028_update_cart_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='clean_cost_eur',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='\u0427\u0438\u0441\u0442\u0430\u044f \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c, eur.'),
        ),
        migrations.AddField(
            model_name='cart',
            name='clean_cost_rub',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='\u0427\u0438\u0441\u0442\u0430\u044f \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c, rub.'),
        ),
        migrations.AddField(
            model_name='cart',
            name='clean_cost_usd',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='\u0427\u0438\u0441\u0442\u0430\u044f \u0441\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c, usd.'),
        ),
        migrations.AddField(
            model_name='cart',
            name='delivery_cost_eur',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0434\u043e\u0441\u0442\u0430\u0432\u043a\u0438, eur.'),
        ),
        migrations.AddField(
            model_name='cart',
            name='delivery_cost_rub',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0434\u043e\u0441\u0442\u0430\u0432\u043a\u0438, rub.'),
        ),
        migrations.AddField(
            model_name='cart',
            name='delivery_cost_usd',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u0434\u043e\u0441\u0442\u0430\u0432\u043a\u0438, usd.'),
        ),
    ]
