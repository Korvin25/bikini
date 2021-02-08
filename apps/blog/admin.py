# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modeltranslation.admin import TranslationInlineModelAdmin, TabbedTranslationAdmin

from ..content.models import Video
from .models import Category, Post, GalleryPhoto, PostComment
from .translation import *  # noqa


admin.site.site_header = 'Bikinimini.ru'


@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    list_display = ('title', 'slug',)
    suit_form_tabs = (
        ('default', 'Категория'),
        ('seo', 'SEO'),
        ('seo-regions', 'SEO (регионы)'),
    )
    fieldsets = (
        ('Категория', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('title', 'slug',),
        }),
        ('SEO', {
            'classes': ('suit-tab suit-tab-seo',),
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',),
        }),
        ('SEO: Санкт-Петербург', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_spb', 'meta_desc_spb', 'meta_keyw_spb', 'h1_spb', 'seo_text_spb',),
        }),
        ('SEO: Новосибирск', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_nsk', 'meta_desc_nsk', 'meta_keyw_nsk', 'h1_nsk', 'seo_text_nsk',),
        }),
        ('SEO: Самара', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sam', 'meta_desc_sam', 'meta_keyw_sam', 'h1_sam', 'seo_text_sam',),
        }),
        ('SEO: Сочи', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sch', 'meta_desc_sch', 'meta_keyw_sch', 'h1_sch', 'seo_text_sch',),
        }),
        ('SEO: Симферополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_smf', 'meta_desc_smf', 'meta_keyw_smf', 'h1_smf', 'seo_text_smf',),
        }),
        ('SEO: Севастополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_svs', 'meta_desc_svs', 'meta_keyw_svs', 'h1_svs', 'seo_text_svs',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'slug', ]


class PostGalleryInline(admin.StackedInline):
    model = GalleryPhoto
    fields = ('photo', 'order', 'show_at_blog', 'add_dt',)
    readonly_fields = ('add_dt',)
    suit_classes = 'suit-tab suit-tab-gallery'
    min_num = 0
    extra = 1


class PostVideoInline(TranslationInlineModelAdmin, admin.StackedInline):
    model = Video
    fields = ('title', 'slug', 'video', 'cover', 'text', 'show_at_list')
    prepopulated_fields = {'slug': ('title',)}
    suit_classes = 'suit-tab suit-tab-video'
    min_num = 0
    extra = 1


class PostCommentInline(admin.StackedInline):
    model = PostComment
    fields = ('lang', 'profile', 'name', 'comment', 'datetime', 'show',)
    readonly_fields = ('profile', 'name', 'comment', 'datetime',)
    suit_classes = 'suit-tab suit-tab-comments'
    min_num = 0
    extra = 0

    def has_add_permission(self, request):
        return None

    # def has_delete_permission(self, request, obj=None):
    #     return None


@admin.register(Post)
class PostAdmin(TabbedTranslationAdmin):
    list_display = ('id', 'title_ru', 'slug_ru', 'category', 'cover', 'cover', 'datetime',)
    list_display_links = ('id', 'title_ru')
    list_filter = ('category', 'datetime',)
    suit_form_tabs = (
        ('default', 'Пост'),
        ('seo', 'SEO'),
        ('seo-regions', 'SEO (регионы)'),
        ('gallery', 'Галерея'),
        ('video', 'Видео'),
        ('comments', 'Комментарии'),
    )
    fieldsets = (
        ('Пост', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('category', 'title', 'slug', 'cover', 'cover_attributes', 'description', 'text', 'datetime',),
        }),
        ('SEO', {
            'classes': ('suit-tab suit-tab-seo',),
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',),
        }),
        ('SEO: Санкт-Петербург', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_spb', 'meta_desc_spb', 'meta_keyw_spb', 'h1_spb', 'seo_text_spb',),
        }),
        ('SEO: Новосибирск', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_nsk', 'meta_desc_nsk', 'meta_keyw_nsk', 'h1_nsk', 'seo_text_nsk',),
        }),
        ('SEO: Самара', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sam', 'meta_desc_sam', 'meta_keyw_sam', 'h1_sam', 'seo_text_sam',),
        }),
        ('SEO: Сочи', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sch', 'meta_desc_sch', 'meta_keyw_sch', 'h1_sch', 'seo_text_sch',),
        }),
        ('SEO: Симферополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_smf', 'meta_desc_smf', 'meta_keyw_smf', 'h1_smf', 'seo_text_smf',),
        }),
        ('SEO: Севастополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_svs', 'meta_desc_svs', 'meta_keyw_svs', 'h1_svs', 'seo_text_svs',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PostGalleryInline, PostVideoInline, PostCommentInline, ]
    search_fields = ['title', 'slug', 'description', 'text', ]


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('datetime', 'name', 'comment', 'post', 'lang', 'profile', 'show',)
    list_editable = ('show',)
    list_filter = ('lang', 'show', 'post',)
    list_per_page = 200
    fieldsets = (
        (None, {
            'fields': ('post', 'lang', 'profile',),
        }),
        ('Данные из формы', {
            'fields': ('name', 'comment',),
        }),
        ('Настройки показа на сайте', {
            'fields': ('datetime', 'show',),
        }),
    )
    readonly_fields = ('post', 'lang', 'profile', 'datetime',)
    search_fields = ['post__title', 'profile__email', 'name', 'comment', ]

    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None
