# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy
import os
from time import time

from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView, TemplateView
from django.views.decorators.csrf import csrf_exempt

from PIL import Image
import pytils



class PhotoUploadView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PhotoUploadView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        http://ishcray.com/downloading-and-saving-image-to-imagefield-in-django
        """
        if request.user.is_anonymous():
            return JsonResponse({'files': [{'name': 'error', 'error': 'Войдите на сайт для загрузки картинок'}], })

        files = []
        # for photo in request.FILES.getlist('file'):
        for photo in request.FILES.values():
            photo_dict = {
                'name': photo.name.replace(' ', '_'),
                'size': photo.size,
            }
            try:
                img = Image.open(photo)
                img_copy = copy.copy(img)
            except IOError:
                photo_dict['error'] = 'Пожалуйста, выберите корректное изображение'
                # files.append(photo_dict)
                continue

            # img_format = self.valid_img(img_copy)
            # if img_format:
            #     photo_dict['type'] = 'image/{0}'.format(img_format.lower())
            #     photo_dict['url'] = self.save_file(request, photo)
            #     files.append(photo_dict['url'])
            # else:
            #     photo_dict['error'] = 'Пожалуйста, выберите корректное изображение'

            photo_dict['url'] = self.save_file(request, photo)
            files.append(photo_dict['url'])

            # files.append(photo_dict)
        # return JsonResponse({'files': files})
        return HttpResponse(';'.join(files))

    def valid_img(self, img):
        """Verifies that an instance of a PIL Image Class is actually an image and returns either True or False."""
        file_type = img.format
        if file_type in ('GIF', 'JPEG', 'JPG', 'PNG'):
            try:
                img.verify()
                return file_type
            except:
                return ''
        else:
            return ''

    def save_file(self, request, photo):
        name, ext = os.path.splitext(photo.name)
        name = pytils.translit.translify(name).replace(' ', '_').replace("'", '_')
        path = 'media/uploads/{}_{}{}'.format(name, int(time()), ext)
        destination = open(path, 'wb+')
        for chunk in photo.chunks():
            destination.write(chunk)
        destination.close()
        return '/' + path
