# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0015_settings_whatsapp_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='whatsapp_phone_de',
            field=models.CharField(default='+7 902 354-38-45', max_length=127, null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0432 Whatsapp'),
        ),
        migrations.AddField(
            model_name='settings',
            name='whatsapp_phone_en',
            field=models.CharField(default='+7 902 354-38-45', max_length=127, null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0432 Whatsapp'),
        ),
        migrations.AddField(
            model_name='settings',
            name='whatsapp_phone_es',
            field=models.CharField(default='+7 902 354-38-45', max_length=127, null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0432 Whatsapp'),
        ),
        migrations.AddField(
            model_name='settings',
            name='whatsapp_phone_fr',
            field=models.CharField(default='+7 902 354-38-45', max_length=127, null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0432 Whatsapp'),
        ),
        migrations.AddField(
            model_name='settings',
            name='whatsapp_phone_it',
            field=models.CharField(default='+7 902 354-38-45', max_length=127, null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0432 Whatsapp'),
        ),
        migrations.AddField(
            model_name='settings',
            name='whatsapp_phone_ru',
            field=models.CharField(default='+7 902 354-38-45', max_length=127, null=True, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0432 Whatsapp'),
        ),
    ]
