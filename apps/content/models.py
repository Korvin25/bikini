# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor_uploader.fields import RichTextUploadingField
from easy_thumbnails.fields import ThumbnailerImageField

from ..catalog.models import Product
from ..core.utils import get_youtube_video_id, get_youtube_embed_video
from ..settings.models import MetatagModel


class Video(models.Model):
    title = models.CharField('Название', max_length=255)
    video = models.URLField('Видео', help_text='Ссылка на youtube.com')
    video_id = models.CharField(null=True, blank=True, max_length=31, editable=False)
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

    def get_cover_url(self):
        return (self.cover.url if self.cover
                else 'http://img.youtube.com/vi/{}/mqdefault.jpg'.format(self.video_id))

    def get_iframe_video_link(self):
        return get_youtube_embed_video(video_id=self.video_id)


class HomepageSlider(models.Model):
    SLIDER_TYPES = (
        ('unit', 'единичный'),
        ('composite', 'составной (поля добавятся позже)'),
    )
    title = models.CharField('Заголовок слайда', max_length=255)
    slider_type = models.CharField('Тип слайда', max_length=15, choices=SLIDER_TYPES, default='unit')
    description = RichTextUploadingField('Описание', blank=True)
    description_h1 = models.CharField('Описание (h1)', max_length=255, blank=True)
    description_picture = ThumbnailerImageField('Описание (картинка)', upload_to='homepage_slider/pictures/',
                                                null=True, blank=True)
    description_picture_alt = models.CharField('Описание (alt у картинки)', max_length=127, blank=True)
    description_p = models.TextField('Описание (текст)', blank=True)
    link = models.URLField('Ссылка')
    link_text = models.CharField('Текст на ссылке', max_length=127, help_text='например, "Перейти в каталог"')
    cover = ThumbnailerImageField('Обложка', upload_to='homepage_slider/covers/', null=True, blank=True)
    video = models.URLField('Видео', help_text='Ссылка на youtube.com', null=True, blank=True)
    video_id = models.CharField(null=True, blank=True, max_length=31, editable=False)
    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', '-add_dt', ]
        verbose_name = 'слайд'
        verbose_name_plural = 'промо-слайдер на главной'

    def __unicode__(self):
        return self.title

    def get_cover_url(self):
        return (self.cover['homepage_cover'].url if self.cover
                else 'http://img.youtube.com/vi/{}/mqdefault.jpg'.format(self.video_id))

    def get_iframe_video_link(self):
        return get_youtube_embed_video(video_id=self.video_id)


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
