# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor_uploader.fields import RichTextUploadingField
from easy_thumbnails.fields import ThumbnailerImageField
from embed_video.fields import EmbedVideoField

from ..catalog.models import Product
from ..settings.models import MetatagModel


class Video(models.Model):
    title = models.CharField('Название', max_length=255)
    video = EmbedVideoField('Ссылка на видео')
    cover = ThumbnailerImageField('Обложка', upload_to='videos/covers/', null=True, blank=True)
    text = RichTextUploadingField('Текст', blank=True, null=True)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='videos', null=True, blank=True)
    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', '-add_dt', ]
        verbose_name = 'видео'
        verbose_name_plural = 'видео'

    def __unicode__(self):
        return self.title

    # def get_cover_url(self):
    #     return (self.cover.url if self.cover
    #             else 'http://img.youtube.com/vi/{}/mqdefault.jpg'.format(self.video_id))


class Page(MetatagModel):
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('Адрес в url', max_length=255, unique=True)
    image = models.ImageField('Картинка', null=True, blank=True)
    image_attributes = models.CharField('Атрибуты alt и title у картинки',
                                        max_length=255, blank=True,
                                        help_text='По умолчанию берутся из поля "Заголовок"')
    text = RichTextUploadingField('Текст')
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'title', ]
        verbose_name = 'страница'
        verbose_name_plural = 'текстовые страницы'

    def __unicode__(self):
        return self.title

    # def get_absolute_url(self):
    #     return reverse('page', kwargs={'slug': self.slug})

    @property
    def image_alt(self):
        return self.image_attributes or self.title


class Menu(models.Model):
    title = models.CharField('Название', max_length=255)
    slug = models.SlugField('Уникальный идентификатор', unique=True)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'меню'
        verbose_name_plural = 'меню'

    def __unicode__(self):
        return self.title


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, verbose_name='Меню', related_name='items')
    label = models.CharField('Название', max_length=255)
    link = models.CharField('Ссылка', max_length=255)
    target_blank = models.BooleanField('Открывать в новой вкладке', default=False)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'пункт меню'
        verbose_name_plural = 'пункты меню'

    def __unicode__(self):
        return self.label
