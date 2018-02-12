# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ckeditor_uploader.fields import RichTextUploadingField
from easy_thumbnails.fields import ThumbnailerImageField

from ..catalog.models import Product
from ..lk.models import Profile
from ..settings.models import Setting, SEOSetting, MetatagModel


class Contest(MetatagModel):
    STATUS_CHOICES = (
        ('active', 'Активен'),
        ('archived', 'В архиве'),
    )
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='active')
    show = models.BooleanField('Опубликован?', default=True)

    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('В url', max_length=255, unique=True)
    cover = ThumbnailerImageField('Обложка', upload_to='contests/covers/')
    list_cover = ThumbnailerImageField('Обложка в списке (вертикальная)', upload_to='contests/covers/',
                                       null=True, blank=True)
    terms = RichTextUploadingField('Условия конкурса', blank=True)

    winner = models.ForeignKey('Participant', null=True, blank=True,
                               verbose_name='Победитель', related_name='victorious_contests')

    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)
    published_dt = models.DateTimeField('Дата публикации', default=timezone.now)
    accepting_to = models.DateField('Конец приема заявок', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', '-published_dt', ]
        verbose_name = 'конкурс'
        verbose_name_plural = 'конкурсы'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        For sitemap.xml lastmod purposes
        """
        SEOSetting.objects.get(key='contests').save()
        return super(Contest, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('contests:contest', kwargs={'slug': self.slug})

    def get_meta_title(self):
        if self.meta_title:
            return self.meta_title
        contests_label = _('Конкурсы')
        title_suffix = Setting.get_seo_title_suffix()
        return '{} — {} — {}'.format(self.title, contests_label, title_suffix)

    @property
    def is_published(self):
        return self.published_dt and self.published_dt <= timezone.now()

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def accepting_enabled(self):
        return (self.is_active
                and (not self.accepting_to or self.accepting_to >= timezone.localtime(timezone.now()).date()))

    @property
    def show_terms(self):
        return bool(not self.winner and self.terms)

    @property
    def participants_profiles(self):
        return self.participants.values_list('profile_id', flat=True)

    @property
    def cover_url(self):
        return self.cover['contest_cover'].url

    @property
    def list_cover_url(self):
        cover = self.list_cover or self.cover
        return cover['contest_list_cover'].url


class ContestTitleLine(models.Model):
    contest = models.ForeignKey(Contest, verbose_name='Конкурс', related_name='title_lines')
    line = models.CharField('Строка', max_length=255)
    big = models.BooleanField('Крупный шрифт?', default=False)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'строка'
        verbose_name_plural = 'строки в заголовке'

    def __unicode__(self):
        return self.line


class Participant(MetatagModel):
    contest = models.ForeignKey(Contest, verbose_name='Конкурс', related_name='participants')
    profile = models.ForeignKey(Profile, verbose_name='Профиль', related_name='contests_participants')

    name = models.CharField('Имя', max_length=255)
    description = models.TextField('Описание', max_length=1000, blank=True)
    photo = ThumbnailerImageField('Фото', upload_to='contests/participants/')

    likes = models.IntegerField('Количество лайков', default=0)
    additional_likes = models.IntegerField('Увеличить на', default=0)
    decreased_likes = models.IntegerField('Уменьшить на', default=0)
    likes_count = models.IntegerField('Общее количество лайков', default=0)

    products = models.ManyToManyField(Product, verbose_name='Товары', blank=True, related_name='contests_participants')
    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['contest', '-likes_count', 'id', ]
        unique_together = ('contest', 'profile',)
        verbose_name = 'участник'
        verbose_name_plural = 'участники'

    def __unicode__(self):
        participant_str = 'кол-во лайков'
        return '{} ({}: {})'.format(self.name, participant_str, self.likes_count)

    def save(self, *args, **kwargs):
        self.contest.save()
        likes_count = self.likes + self.additional_likes - self.decreased_likes
        if likes_count < 0:
            likes_count = 0
        self.likes_count = likes_count
        return super(Participant, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('contests:participant', kwargs={'contest_slug': self.contest.slug, 'pk': self.id})

    def get_title(self):
        return self.name

    def get_meta_title(self):
        return (self.meta_title if self.meta_title
                else '{} — {}'.format(self.name, self.contest.get_meta_title()))

    def get_meta_keyw(self):
        return self.contest.get_meta_keyw()

    def get_meta_desc(self):
        return self.contest.get_meta_desc()

    def get_likes(self):
        return self.likes_count if self.likes_count >= 0 else 0

    @property
    def is_winner(self):
        return self.contest.status == 'active' and self.contest.winner_id == self.id

    @property
    def cover_url(self):
        return self.photo['participant_cover'].url

    @property
    def cover_winner_url(self):
        return self.photo['participant_cover_winner'].url

    @property
    def photo_preview_url(self):
        return self.photo['participant_photo_preview'].url

    @property
    def photo_thumb_url(self):
        return self.photo['participant_photo_thumb'].url

    @property
    def photo_big_url(self):
        return self.photo['participant_photo_big'].url


class ParticipantPhoto(models.Model):
    participant = models.ForeignKey(Participant, verbose_name='Участник', related_name='photos')
    photo = ThumbnailerImageField('Фото', upload_to='contests/participants/')

    class Meta:
        ordering = ['id', ]
        verbose_name = 'фото'
        verbose_name_plural = 'фото'

    def __unicode__(self):
        return '#{}: {}'.format(self.id, self.photo.name)

    @property
    def photo_preview_url(self):
        return self.photo['participant_photo_preview'].url

    @property
    def photo_thumb_url(self):
        return self.photo['participant_photo_thumb'].url

    @property
    def photo_big_url(self):
        return self.photo['participant_photo_big'].url
