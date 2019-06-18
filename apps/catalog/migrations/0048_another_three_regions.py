# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0047_product_sale'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='h1_sch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='category',
            name='h1_smf',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='category',
            name='h1_svs',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_desc_sch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_desc_smf',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_desc_svs',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_keyw_sch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_keyw_smf',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_keyw_svs',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_title_sch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_title_smf',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_title_svs',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='category',
            name='seo_text_sch',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='category',
            name='seo_text_smf',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='category',
            name='seo_text_svs',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='h1_sch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='product',
            name='h1_smf',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='h1_svs',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_desc_sch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_desc_smf',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_desc_svs',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_keyw_sch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_keyw_smf',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_keyw_svs',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_title_sch',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_title_smf',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_title_svs',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='seo_text_sch',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u043e\u0447\u0438)'),
        ),
        migrations.AddField(
            model_name='product',
            name='seo_text_smf',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)'),
        ),
        migrations.AddField(
            model_name='product',
            name='seo_text_svs',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)'),
        ),
    ]
