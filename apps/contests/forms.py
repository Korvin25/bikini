# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Contest, Participant


class ContestAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ContestAdminForm, self).__init__(*args, **kwargs)
        self.fields['winner'].queryset = self.instance.participants.all()


class ContestApplyForm(forms.ModelForm):

    class Meta:
        fields = ('contest', 'profile', 'name', 'description',)
        model = Participant

    def clean_contest(self):
        contest = self.cleaned_data.get('contest')
        if not contest.accepting_enabled:
            raise forms.ValidationError('Заявки на участие в конкурсе больше не принимаются.')
        return contest

    def clean_profile(self):
        profile = self.cleaned_data.get('profile')
        contest = self.cleaned_data.get('contest')
        if contest and profile.id in contest.participants_profiles:
            raise forms.ValidationError('Вы уже принимаете участие в конурсе.')
        return profile
