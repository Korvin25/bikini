# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from ckeditor.fields import RichTextField

from ..lk.models import Profile
from ..settings.models import MetatagModel


class Contest(MetatagModel):
    STATUS_CHOICES = (
        ('active', 'Активен'),
        ('archived', 'В архиве'),
    )
    sponsors = models.ManyToManyField(Profile, verbose_name='Спонсоры', related_name='contest_sponsors',
                                      limit_choices_to={'profile_type': 'company'}, blank=True)
    jury = models.ManyToManyField(Profile, verbose_name='Жюри', related_name='contest_jury',
                                  limit_choices_to={'profile_type': 'human'}, blank=True)

    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default='active')
    show = models.BooleanField('Опубликован?', default=True)

    ru = models.BooleanField('ru', default=True)
    en = models.BooleanField('en', default=False)

    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('В url', max_length=255, unique=True)
    cover = models.ImageField('Обложка', upload_to='contests/covers/')
    cover_title = models.CharField('Атрибут title у обложки', max_length=255, blank=True,
                                   help_text='По умолчанию берется из поля "Заголовок"')

    terms = RichTextField('Условия участия')

    branding_title = models.CharField('Генеральный спонсор (название'), max_length=255, null=True, blank=True)
    branding_link = models.URLField('Генеральный спонсор (ссылка'), max_length=255, null=True, blank=True)
    branding_cover = models.ImageField('Обложка', upload_to='branding/contests/', null=True, blank=True)

    first_place = models.ForeignKey('Participant', null=True, blank=True,
                                    verbose_name='Первое место', related_name='first_place')
    second_place = models.ForeignKey('Participant', null=True, blank=True,
                                     verbose_name='Второе место', related_name='second_place')
    third_place = models.ForeignKey('Participant', null=True, blank=True,
                                    verbose_name='Третье место', related_name='third_place')

    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)
    published_dt = models.DateTimeField('Дата публикации', default=timezone.now)
    accepting_to = models.DateField('Конец приема заявок')

    objects = models.Manager()
    i18n_objects = I18nManager()
    sitemap_objects = SitemapManager()

    class Meta:
        ordering = ['-published_dt', ]
        verbose_name = "конкурс"
        verbose_name_plural = "конкурсы"

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        # return reverse('contests:contest', kwargs={'pk': self.pk})
        return reverse('contests:contest', kwargs={'slug': self.slug})

    # def get_meta_title(self):
    #     return (self.meta_title if self.meta_title
    #             else '{0} — {1} — Jobroom'.format(self.title, 'Конкурсы'))

    @property
    def is_published(self):
        return self.published_dt and self.published_dt <= timezone.now()

    @property
    def is_active(self):
        return self.status == 'active'

    @property
    def accepting_enabled(self):
        return self.accepting_to and self.accepting_to >= timezone.localtime(timezone.now()).date() and self.is_active

    def get_cover(self):
        return self.branding_cover or self.cover

    def get_cover_title(self):
        return self.cover_title or self.title

    @property
    def winners(self):
        winners = [self.first_place, self.second_place, self.third_place]
        return [winner for winner in winners if winner]

    def show_sponsors(self):
        return ', '.join([profile.__unicode__() for profile in self.sponsors.all()])
    show_sponsors.allow_tags = True
    show_sponsors.short_description = 'Спонсоры'

    def show_jury(self):
        return ', '.join([profile.__unicode__() for profile in self.jury.all()])
    show_jury.allow_tags = True
    show_jury.short_description = 'Жюри'


class Participant(MetatagModel):
    contest = models.ForeignKey(Contest, verbose_name='Конкурс')
    profile = models.ForeignKey(Profile, verbose_name='Профиль')
    # photo = models.ImageField('Фото', upload_to='contests/participants/')
    photo = ResizedImageField('Фото', size=[591, 380], quality=100,
                              upload_to='contests/participants/', null=True, blank=True)
    photo_thumb = models.ImageField('Фото (миниатюра для вывода в списке участников'), 
                                    upload_to='contests/participants/thumbs/', null=True, blank=True,
                                    help_text='При выводе на сайте будет обрезано до 290x224 px. Если не выбрано, будет выводиться обычное фото.')
    # likes = models.ManyToManyField(Profile, verbose_name='Список лайкнувших', related_name='contest_likes', blank=True)
    likes = models.IntegerField('Количество лайков', default=0)
    additional_likes = models.IntegerField('Увеличить на', default=0)
    decreased_likes = models.IntegerField('Уменьшить на', default=0)
    likes_count = models.IntegerField('Общее количество лайков', default=0)

    class Meta:
        ordering = ['contest', '-likes_count', 'id', ]
        unique_together = ('contest', 'profile',)
        verbose_name = "участник"
        verbose_name_plural = "участники"

    def __unicode__(self):
        participant_str = 'кол-во лайков'
        if self.profile:
            return '{0} ({1}: {2})'.format(self.profile, participant_str, self.likes_count)
        else:
            return '{1}: {2}'.format(participant_str, self.likes_count)

    def save(self, *args, **kwargs):
        # if self.id:
        #     likes_count = self.likes + self.additional_likes - self.decreased_likes
        #     if likes_count < 0:
        #         likes_count = 0
        #     self.likes_count = likes_count
        likes_count = self.likes + self.additional_likes - self.decreased_likes
        if likes_count < 0:
            likes_count = 0
        self.likes_count = likes_count
        return super(Participant, self).save(*args, **kwargs)

    def get_absolute_url(self):
        # return reverse('contests:participant', kwargs={'contest_id': self.contest_id, 'pk': self.profile_id})
        return reverse('contests:participant', kwargs={'contest_slug': self.contest.slug, 'pk': self.profile_id})

    @property
    def thumb_url(self):
        thumb = self.photo_thumb if self.photo_thumb else self.photo
        return get_thumbnail(thumb, '290x224', crop='center').url

    # def contest_name(self):
    #     return self.contest.__unicode__() if self.contest else '-'
    # contest_name.short_description = 'Название конкурса'
    # contest_name.allow_tags = True

    def profile_name(self):
        return self.profile.__unicode__() if self.profile else '-'
    profile_name.short_description = 'Имя участника'
    profile_name.allow_tags = True

    def thumb_tag(self):
        thumb_url = self.thumb_url
        return '<img src="{0}" />'.format(thumb_url) if thumb_url else 'Нет фото'
    thumb_tag.short_description = 'Текущая миниатюра'
    thumb_tag.allow_tags = True

    def photo_tag(self):
        photo_url = get_thumbnail(self.photo, '591', crop='center').url
        return '<img src="{0}" />'.format(photo_url)
    photo_tag.short_description = 'Текущее фото'
    photo_tag.allow_tags = True

    def link(self):
        if self.id:
            return '<a href="http://jobroom.ru/jbrm-adm/contests/participant/{0}/">http://jobroom.ru/jbrm-adm/contests/participant/{0}/</a>'.format(self.id)
        else:
            return '-'
    link.short_description = 'Ссылка в админке'
    link.allow_tags = True

    @property
    def title(self):
        return self.profile

    def get_meta_title(self):
        return (self.meta_title if self.meta_title
                else '{0} — {1} — Jobroom'.format(self.title, self.contest))

    def get_meta_keyw(self):
        return self.contest.get_meta_keyw()

    def get_meta_desc(self):
        return self.contest.get_meta_desc()

    def get_likes(self):
        return self.likes_count if self.likes_count >= 0 else 0

    # def show_likes_count(self):
    #     return self.likes.count() + self.additional_likes - self.decreased_likes
    # show_likes_count.allow_tags = True
    # show_likes_count.short_description = 'Кол-во лайков'

    def winner_place(self):
        return (0 if self.contest.status == 'active'
                else 1 if self.first_place.count()
                else 2 if self.second_place.count()
                else 3 if self.third_place.count()
                else 0)


class ParticipantComment(models.Model):
    RU_EN_CHOICES = (
        ('ru', 'ru'),
        ('en', 'en'),
    )
    participant = models.ForeignKey(Participant, verbose_name='Участник', related_name='comments')
    profile = models.ForeignKey(Profile, verbose_name='Кто написал', related_name='contest_comments')
    ru_en = models.CharField('Языковой раздел', max_length=2, choices=RU_EN_CHOICES)

    datetime = models.DateTimeField('Дата добавления', auto_now_add=True)
    comment = models.TextField('Текст комментария')
    show = models.BooleanField('Опубликован', default=True)

    objects = CommentManager()

    class Meta:
        ordering = ['-datetime']
        verbose_name = "комментарий"
        verbose_name_plural = "участники: комментарии"

    def __unicode__(self):
        return '#{0} ({1})'.format(self.id, self.datetime)

    def show_contest(self):
        return self.participant.contest
    show_contest.allow_tags = True
    show_contest.short_description = 'Конкурс'

    def show_participant(self):
        return self.participant.profile
    show_participant.allow_tags = True
    show_participant.short_description = 'Участник'
