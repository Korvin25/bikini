# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ckeditor_uploader.fields import RichTextUploadingField
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer
from filer.fields.image import FilerImageField

from ..core.regions_utils import region_field
from ..lk.models import Profile
from ..settings.models import Setting, SEOSetting, MetatagModel


class Category(MetatagModel):
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('Адрес в url', max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title', ]
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        For sitemap.xml lastmod purposes
        """
        SEOSetting.objects.get(key='blog').save()
        return super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})

    def get_meta_title(self):
        meta_title = region_field(self, 'meta_title')
        if meta_title:
            return meta_title

        blog_label = _('Блог')
        title_suffix = Setting.get_seo_title_suffix()
        return '{} — {} — {}'.format(self.title, blog_label, title_suffix)


class Post(MetatagModel):
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='posts')
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('Адрес в url', max_length=255, unique=True)
    cover = ThumbnailerImageField('Обложка')
    cover_attributes = models.CharField('Атрибуты alt и title у обложки',
                                        max_length=255, blank=True,
                                        help_text='По умолчанию берутся из поля "Заголовок"')
    description = models.TextField('Краткое описание')
    text = RichTextUploadingField('Текст')
    datetime = models.DateTimeField('Дата и время публикации', default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-datetime', ]
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        For sitemap.xml lastmod purposes
        """
        self.category.save()
        return super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post', kwargs={'year': self.datetime.strftime('%Y'),
                                            'month': self.datetime.strftime('%m'),
                                            'slug': self.slug,
                                            'pk': self.id})

    def get_meta_title(self):
        meta_title = region_field(self, 'meta_title')
        if meta_title:
            return meta_title
        return '{} — {}'.format(self.title, self.category.get_meta_title())

    @property
    def cover_list_url(self):
        return self.cover['blog_cover_list'].url

    @property
    def cover_detail_url(self):
        return self.cover['blog_cover_detail'].url

    @property
    def cover_alt(self):
        return self.cover_attributes or self.title

    @property
    def shown_comments(self):
        return self.comments.filter(show=True)


class GalleryPhoto(models.Model):
    post = models.ForeignKey(Post, verbose_name='Пост', related_name='gallery')
    photo = FilerImageField(verbose_name='Фото')

    order = models.IntegerField('Порядок', default=10)
    show_at_blog = models.BooleanField('Показывать на странице блога', default=True)
    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        ordering = ['order', 'add_dt', ]
        verbose_name = 'фото'
        verbose_name_plural = 'галерея'

    def __unicode__(self):
        return '#{}'.format(self.id)

    @property
    def thumb_url(self):
        return get_thumbnailer(self.photo)['blog_gallery_thumb'].url

    @property
    def big_url(self):
        return get_thumbnailer(self.photo)['product_photo_big'].url


class PostComment(models.Model):
    post = models.ForeignKey(Post, verbose_name='Пост', related_name='comments')
    lang = models.CharField('Язык', default='ru', max_length=4, choices=settings.LANGUAGES)

    profile = models.ForeignKey(Profile, verbose_name='Профиль', related_name='comments', null=True, blank=True)
    name = models.CharField('Имя', max_length=255)
    comment = models.TextField('Комментарий', max_length=32768)

    datetime = models.DateTimeField('Дата и время', auto_now=True)
    show = models.BooleanField('Показывать на сайте', default=True)

    class Meta:
        ordering = ['datetime', ]
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __unicode__(self):
        return '{} к посту {} ({})'.format(self.name, self.post.title, self.datetime.strftime('%d.%m.%Y'))

    def save(self, *args, **kwargs):
        """
        For sitemap.xml lastmod purposes
        """
        self.post.save()
        return super(PostComment, self).save(*args, **kwargs)
