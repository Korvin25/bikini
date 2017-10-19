# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Video, HomepageSlider
from ..core.utils import get_youtube_video_id, get_vimeo_id


class VideoAdminForm(forms.ModelForm):
    video_id = 0

    class Meta:
        model = Video
        fields = '__all__'

    def clean_video(self):
        video = self.cleaned_data.get('video')
        self.video_id = get_youtube_video_id(video)
        if not self.video_id:
            raise forms.ValidationError('Укажите валидную ссылку на youtube-видео.')
        return video

    def save(self, *args, **kwargs):
        obj = super(VideoAdminForm, self).save(*args, **kwargs)
        if self.video_id:
            obj.video_id = self.video_id
        obj.save()
        return obj


class HomepageSliderForm(forms.ModelForm):
    video_id = 0

    class Meta:
        model = HomepageSlider
        fields = '__all__'

    def clean_video(self):
        video = self.cleaned_data.get('video')
        cover = self.cleaned_data.get('cover')
        self.video_id = get_youtube_video_id(video)
        if not (self.video_id or cover):
            raise forms.ValidationError('Загрузите обложку или укажите валидную ссылку на youtube-видео.')
        return video

    def save(self, *args, **kwargs):
        obj = super(VideoAdminForm, self).save(*args, **kwargs)
        if self.video_id:
            obj.video_id = self.video_id
        obj.save()
        return obj
