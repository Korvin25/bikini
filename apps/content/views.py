# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.views.generic import TemplateView, DetailView

from el_pagination.views import AjaxListView

from ..banners.models import PromoBanner
from ..catalog.models import Product
from ..core.http_utils import get_object_from_slug_and_kwargs
from ..settings.models import Settings
from .models import Video, Page


class HomepageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        banner = PromoBanner.objects.prefetch_related('girls').filter(is_enabled=True).order_by('?').first()
        if not banner:
            banner = PromoBanner.objects.prefetch_related('girls').all().order_by('?').first()
        products = Product.shown()\
                          .filter(show=True, show_at_homepage=True)\
                          .order_by('order_at_homepage', 'order', '-id')
        context = {
            'promo_banner': banner,
            'products': products,
        }
        context.update(super(HomepageView, self).get_context_data(**kwargs))
        return context


class VideoListView(AjaxListView):
    template_name = "video/videos.html"
    page_template = 'video/include/videos.html'
    model = Video
    context_object_name = 'videos'

    def get_queryset(self, **kwargs):
        return self.model.objects.filter(show_at_list=True)


class VideoDetailView(DetailView):
    template_name = 'video/video.html'
    model = Video
    context_object_name = 'video'

    def get_object(self, *args, **kwargs):
        kw = {'pk': self.kwargs.get('pk')}
        video = get_object_from_slug_and_kwargs(self.request, model=Video, slug=self.kwargs.get('slug'), **kw)
        return video


class PageView(DetailView):
    template_name = 'page.html'
    model = Page
    context_object_name = 'page'


def robots_txt(request):
    txt = Settings.get_robots_txt()
    txt = txt or '\r\n'.join(['User-agent: *',
                              'Disallow: ',
                              'Host: {host}',
                              'Sitemap: {scheme}://{host}/sitemap.xml',])
    txt = txt.format(host=request.get_host(), scheme=request.scheme)
    return HttpResponse(txt, content_type='text/plain; charset=utf-8')
