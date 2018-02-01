# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db.models.functions import TruncMonth
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView, DetailView

from ..core.http_utils import get_object_from_slug_and_kwargs
from .models import Category, Post, GalleryPhoto, PostComment


class PostListView(TemplateView):
    with_category = False
    TEMPLATES = {
        'home': 'blog/home.html',
        'category': 'blog/category.html',
        'ajax': 'blog/include/posts.html',
    }

    def get_template_names(self):
        TEMPLATES = self.TEMPLATES
        is_ajax = self.request.is_ajax()
        with_category = self.with_category
        return {
            is_ajax: TEMPLATES['ajax'],
            (not is_ajax and with_category): TEMPLATES['category'],
            (not is_ajax and not with_category): TEMPLATES['home'],
        }.get(True)

    def get_category(self):
        kw = {}
        self.category = None
        if self.with_category is True:
            self.category = get_object_from_slug_and_kwargs(self.request, model=Category, slug=self.kwargs.get('slug'), **kw)
        return self.category

    def get_months(self, qs):
        months = qs.values_list('month', flat=True)
        months = sorted(set(months), reverse=True)
        months_columns = []
        has_months = bool(months)
        if has_months:
            l = ((len(months)/2)+1 if len(months) % 2
                 else len(months)/2)
            months_columns = [months[:l], months[l:]]
        self.has_months = has_months
        self.months_columns = months_columns

    def get_filter(self):
        f = {}
        if self.f.get('q'):
            f['title__icontains'] = self.f['q']
        if self.f.get('year'):
            f['datetime__year'] = self.f['year']
        if self.f.get('month'):
            f['datetime__month'] = self.f['month']
        self.filter = f
        return f

    def get_queryset(self, **kwargs):
        GET = self.request.GET
        self.f = {}

        qs = Post.objects.select_related('category').filter(datetime__lte=timezone.now())
        qs = qs.annotate(month=TruncMonth('datetime'))  # FROM: https://toster.ru/q/366649
        if self.category:
            qs = qs.filter(category_id=self.category.id)

        self.get_months(qs)

        self.f['q'] = GET.get('q')
        try:
            self.f['year'] = int(GET.get('year', 0))
        except ValueError:
            pass
        try:
            self.f['month'] = int(GET.get('month', 0))
        except ValueError:
            pass

        self.month_str = '{}-{}'.format(self.f.get('year', 0), self.f.get('month', 0))

        qs = qs.filter(**self.get_filter()).distinct()
        qs = qs.order_by('-datetime', '-id')

        self.qs = qs
        return qs

    def get_gallery(self):
        photos = GalleryPhoto.objects.filter(show_at_blog=True)
        if self.category:
            photos = photos.select_related('post').filter(post__category_id=self.category.id)
        # photos = photos.filter(post_id__in=self.qs.values_list('id', flat=True))
        return photos.order_by('-id')[:12]

    def get_context_data(self, **kwargs):
        category = self.get_category()
        posts = self.get_queryset()
        gallery = self.get_gallery()
        context = {
            'category': category,
            'posts': posts,
            'f': self.f,
            'filter': self.filter,
            'has_months': self.has_months,
            'months_columns': self.months_columns,
            'month_str': self.month_str,
            'gallery': gallery,
        }
        context.update(super(PostListView, self).get_context_data(**kwargs))
        return context


class PostDetailView(DetailView):
    template_name = 'blog/post.html'
    model = Post
    context_object_name = 'post'

    def get_object(self, *args, **kwargs):
        kw = {
            'datetime__year': self.kwargs.get('year'),
            'datetime__month': self.kwargs.get('month'),
            'pk': self.kwargs.get('pk')
        }
        post = get_object_from_slug_and_kwargs(self.request, model=Post, slug=self.kwargs.get('slug'), **kw)
        return post

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        redirect_url = post.get_absolute_url()

        name = request.POST.get('name')
        comment = request.POST.get('comment')
        profile = request.user if not request.user.is_anonymous() else None

        if name and comment:
            c = PostComment.objects.create(post=post, lang=request.LANGUAGE_CODE,
                                           name=name, comment=comment, profile=profile)
            redirect_url = '{}#comment{}'.format(redirect_url, c.id)

        return HttpResponseRedirect(redirect_url)
