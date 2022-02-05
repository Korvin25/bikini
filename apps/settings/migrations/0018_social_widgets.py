# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0017_settings_percent_marketplays'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='fb_widget',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='settings',
            name='fb_widget_de',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='settings',
            name='fb_widget_en',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='settings',
            name='fb_widget_es',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='settings',
            name='fb_widget_fr',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='settings',
            name='fb_widget_it',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='settings',
            name='fb_widget_ru',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='settings',
            name='ig_widget',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='settings',
            name='ig_widget_de',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='settings',
            name='ig_widget_en',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='settings',
            name='ig_widget_es',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='settings',
            name='ig_widget_fr',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='settings',
            name='ig_widget_it',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='settings',
            name='ig_widget_ru',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='settings',
            name='tw_widget',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', verbose_name='Twitter'),
        ),
        migrations.AddField(
            model_name='settings',
            name='tw_widget_de',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Twitter'),
        ),
        migrations.AddField(
            model_name='settings',
            name='tw_widget_en',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Twitter'),
        ),
        migrations.AddField(
            model_name='settings',
            name='tw_widget_es',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Twitter'),
        ),
        migrations.AddField(
            model_name='settings',
            name='tw_widget_fr',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Twitter'),
        ),
        migrations.AddField(
            model_name='settings',
            name='tw_widget_it',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Twitter'),
        ),
        migrations.AddField(
            model_name='settings',
            name='tw_widget_ru',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='Twitter'),
        ),
        migrations.AddField(
            model_name='settings',
            name='vk_widget',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', verbose_name='VK'),
        ),
        migrations.AddField(
            model_name='settings',
            name='vk_widget_de',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='VK'),
        ),
        migrations.AddField(
            model_name='settings',
            name='vk_widget_en',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='VK'),
        ),
        migrations.AddField(
            model_name='settings',
            name='vk_widget_es',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='VK'),
        ),
        migrations.AddField(
            model_name='settings',
            name='vk_widget_fr',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='VK'),
        ),
        migrations.AddField(
            model_name='settings',
            name='vk_widget_it',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='VK'),
        ),
        migrations.AddField(
            model_name='settings',
            name='vk_widget_ru',
            field=models.TextField(blank=True, default='', help_text='HTML-\u043a\u043e\u0434', null=True, verbose_name='VK'),
        ),
    ]
