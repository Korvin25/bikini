# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0048_another_three_regions'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductTab',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta_title', models.CharField(blank=True, help_text='\u041e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c, \u0447\u0442\u043e\u0431\u044b \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u043f\u043e\u043b\u0435 "\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a"', max_length=255, verbose_name='Meta title')),
                ('meta_desc', models.CharField(blank=True, help_text='\u041e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c, \u0447\u0442\u043e\u0431\u044b \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u043f\u043e\u043b\u0435 "\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a"', max_length=255, verbose_name='Meta description')),
                ('meta_keyw', models.CharField(blank=True, help_text='\u041e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c, \u0447\u0442\u043e\u0431\u044b \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u043f\u043e\u043b\u0435 "\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a"', max_length=255, verbose_name='Meta keywords (\u0447\u0435\u0440\u0435\u0437 \u0437\u0430\u043f\u044f\u0442\u0443\u044e)')),
                ('h1', models.CharField(blank=True, help_text='\u041e\u0441\u0442\u0430\u0432\u044c\u0442\u0435 \u043f\u0443\u0441\u0442\u044b\u043c, \u0447\u0442\u043e\u0431\u044b \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u044c \u043f\u043e\u043b\u0435 "\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a"', max_length=255, verbose_name='H1 (\u043d\u0430 \u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430\u0445, \u0433\u0434\u0435 \u043e\u043d \u043f\u0440\u0435\u0434\u0443\u0441\u043c\u043e\u0442\u0440\u0435\u043d)')),
                ('seo_text', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442')),
                ('meta_title_spb', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u0430\u043d\u043a\u0442-\u041f\u0435\u0442\u0435\u0440\u0431\u0443\u0440\u0433)')),
                ('meta_title_nsk', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u041d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a)')),
                ('meta_title_sam', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u0430\u043c\u0430\u0440\u0430)')),
                ('meta_title_sch', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u043e\u0447\u0438)')),
                ('meta_title_smf', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)')),
                ('meta_title_svs', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta title (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)')),
                ('meta_desc_spb', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u0430\u043d\u043a\u0442-\u041f\u0435\u0442\u0435\u0440\u0431\u0443\u0440\u0433)')),
                ('meta_desc_nsk', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u041d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a)')),
                ('meta_desc_sam', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u0430\u043c\u0430\u0440\u0430)')),
                ('meta_desc_sch', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u043e\u0447\u0438)')),
                ('meta_desc_smf', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)')),
                ('meta_desc_svs', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta description (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)')),
                ('meta_keyw_spb', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u0430\u043d\u043a\u0442-\u041f\u0435\u0442\u0435\u0440\u0431\u0443\u0440\u0433)')),
                ('meta_keyw_nsk', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u041d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a)')),
                ('meta_keyw_sam', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u0430\u043c\u0430\u0440\u0430)')),
                ('meta_keyw_sch', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u043e\u0447\u0438)')),
                ('meta_keyw_smf', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)')),
                ('meta_keyw_svs', models.CharField(blank=True, max_length=255, null=True, verbose_name='Meta keywords (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)')),
                ('h1_spb', models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u0430\u043d\u043a\u0442-\u041f\u0435\u0442\u0435\u0440\u0431\u0443\u0440\u0433)')),
                ('h1_nsk', models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u041d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a)')),
                ('h1_sam', models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u0430\u043c\u0430\u0440\u0430)')),
                ('h1_sch', models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u043e\u0447\u0438)')),
                ('h1_smf', models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)')),
                ('h1_svs', models.CharField(blank=True, max_length=255, null=True, verbose_name='H1 (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)')),
                ('seo_text_spb', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u0430\u043d\u043a\u0442-\u041f\u0435\u0442\u0435\u0440\u0431\u0443\u0440\u0433)')),
                ('seo_text_nsk', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u041d\u043e\u0432\u043e\u0441\u0438\u0431\u0438\u0440\u0441\u043a)')),
                ('seo_text_sam', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u0430\u043c\u0430\u0440\u0430)')),
                ('seo_text_sch', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u043e\u0447\u0438)')),
                ('seo_text_smf', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u0438\u043c\u0444\u0435\u0440\u043e\u043f\u043e\u043b\u044c)')),
                ('seo_text_svs', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='SEO-\u0442\u0435\u043a\u0441\u0442 (\u0421\u0435\u0432\u0430\u0441\u0442\u043e\u043f\u043e\u043b\u044c)')),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_ru', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_en', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_de', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_fr', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_it', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_es', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_ru', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_en', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_de', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_fr', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_it', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_es', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('order', models.IntegerField(default=10, verbose_name='\u041f\u043e\u0440\u044f\u0434\u043e\u043a')),
            ],
            options={
                'ordering': ['order', 'id'],
                'verbose_name': '\u0432\u043a\u043b\u0430\u0434\u043a\u0430',
                'verbose_name_plural': '\u0441\u0442\u0440\u0430\u043d\u0438\u0446\u0430 \u0442\u043e\u0432\u0430\u0440\u0430: \u043e\u0431\u0449\u0438\u0435 \u0432\u043a\u043b\u0430\u0434\u043a\u0438',
            },
        ),
        migrations.CreateModel(
            name='ProductTabSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_ru', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_en', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_de', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_fr', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_it', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_es', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_ru', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_en', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_de', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_fr', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_it', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_es', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('show', models.BooleanField(default=True, verbose_name='\u041f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u0442\u044c \u043d\u0430 \u0441\u0430\u0439\u0442\u0435')),
                ('order', models.IntegerField(default=10, verbose_name='\u041f\u043e\u0440\u044f\u0434\u043e\u043a')),
                ('tab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='catalog.ProductTab', verbose_name='\u0412\u043a\u043b\u0430\u0434\u043a\u0430')),
            ],
            options={
                'ordering': ['order', 'id'],
                'verbose_name': '\u0441\u0435\u043a\u0446\u0438\u044f',
                'verbose_name_plural': '\u0441\u0435\u043a\u0446\u0438\u0438',
            },
        ),
    ]
