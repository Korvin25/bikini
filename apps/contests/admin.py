# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modeltranslation.admin import TranslationInlineModelAdmin, TabbedTranslationAdmin

from ..core.admin import ImageThumbAdminMixin
from .forms import ContestAdminForm
from .models import Contest, ContestTitleLine, Participant, ParticipantPhoto
from .translation import *


class ContestTitleLineInline(TranslationInlineModelAdmin, admin.TabularInline):
    model = ContestTitleLine
    suit_classes = 'suit-tab suit-tab-title-lines'

    def get_extra(self, request, obj=None, **kwargs):
        extra = (0 if obj and obj.title_lines.count()
                 else 1)
        return extra


class ParticipantInline(ImageThumbAdminMixin, TranslationInlineModelAdmin, admin.StackedInline):
    model = Participant
    fields = ('profile', 'name', 'description', 'photo', 'likes', 'additional_likes', 'decreased_likes',
              'products', 'add_dt',)  # 'show_photos'
    raw_id_fields = ('profile', 'products',)
    readonly_fields = ('add_dt', 'likes',)
    suit_classes = 'suit-tab suit-tab-participants'

    def get_extra(self, request, obj=None, **kwargs):
        extra = (0 if obj and obj.participants.count()
                 else 1)
        return extra


@admin.register(Contest)
class ContestAdmin(ImageThumbAdminMixin, TabbedTranslationAdmin):
    list_display = ('title', 'slug', 'status', 'show', 'cover', 'list_cover', 'winner',
                    'add_dt', 'published_dt', 'accepting_to',)
    list_display_links = ('title', 'slug',)
    suit_form_tabs = (('default', 'Конкурс'), ('title-lines', 'Строки в заголовке'),
                      ('participants', 'Участники'), ('seo', 'SEO'),)
    form = ContestAdminForm
    fieldsets = (
        ('Конкурс', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('title', 'slug', 'cover', 'list_cover', 'terms',),
        }),
        ('Победитель', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('winner',),
        }),
        ('Настройки показа на сайте', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('status', 'add_dt', 'published_dt', 'accepting_to',),
        }),
        ('SEO', {
            'classes': ('suit-tab suit-tab-seo',),
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('add_dt',)
    inlines = [ContestTitleLineInline, ParticipantInline, ]
    search_fields = ['title', 'slug', 'terms', ]


class ParticipantPhotoInline(ImageThumbAdminMixin, admin.TabularInline):
    model = ParticipantPhoto
    fields = ('photo',)
    suit_classes = 'suit-tab suit-tab-photos'

    def get_extra(self, request, obj=None, **kwargs):
        extra = (0 if obj and obj.photos.count()
                 else 1)
        return extra


@admin.register(Participant)
class ParticipantAdmin(ImageThumbAdminMixin, TabbedTranslationAdmin):
    list_display = ('contest', 'name', 'profile', 'photo', 'likes_count', 'add_dt',)
    list_display_links = ('contest', 'name',)
    list_filter = ('contest',)
    suit_form_tabs = (('default', 'Участник'), ('photos', 'Фото'), ('seo', 'SEO'),)
    fieldsets = (
        ('Участник', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('contest', 'profile', 'name', 'description', 'photo', 'products', 'add_dt',),
        }),
        ('Лайки', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('likes', 'additional_likes', 'decreased_likes',),
        }),
        ('SEO', {
            'classes': ('suit-tab suit-tab-seo',),
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        }),
    )
    raw_id_fields = ('profile', 'products',)
    readonly_fields = ('add_dt', 'likes', )
    inlines = [ParticipantPhotoInline, ]
    search_fields = ['profile__email', 'profile__name', 'name', 'description', ]
