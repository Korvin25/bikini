# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput, required=False)
    old_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Profile
        fields = ('name', 'country', 'city', 'address', 'phone', 'email',)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        # self.fields['name'].required = True
        # self.fields['country'].required = True
        # self.fields['city'].required = True
        # self.fields['address'].required = True
        # self.fields['phone'].required = True
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != self.instance.email:
            if Profile.objects.filter(email__iexact=email).count():
                raise forms.ValidationError('Такой email уже занят.')
        return email

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if old_password:
            if not self.instance.check_password(old_password):
                raise forms.ValidationError('Неверный пароль.')
        return old_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password', '').strip()
        if new_password:
            old_password = self.cleaned_data.get('old_password')
            if not old_password and self.instance.has_password:
                if self.data.get('old_password'):
                    # значит, старый пароль был неправильный и не попал в self.data
                    return None
                else:
                    raise forms.ValidationError('Введите старый пароль.')
        return new_password

    def save(self, commit=True):
        user = super(ProfileForm, self).save(commit=False)
        if self.cleaned_data.get('email'):
            user.has_email = True
        if self.cleaned_data.get('new_password'):
            user.set_password(self.cleaned_data['new_password'])
            user.has_password = True
        if commit:
            user.save()
        return user
