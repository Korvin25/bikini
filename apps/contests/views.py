# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.files import File
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView, DetailView, View, CreateView

from ..core.http_utils import get_object_from_slug_and_kwargs
from ..core.mixins import JSONFormMixin, GetNotAllowedMixin
from .forms import ContestApplyForm
from .models import Contest, Participant, ParticipantPhoto


class ContestsHomeView(TemplateView):
    template_name = 'contests/contests.html'

    def get_object(self, *args, **kwargs):
        contest = Contest.objects.filter(show=True, published_dt__lte=timezone.now(), status='active').first()
        return contest

    def get_context_data(self, **kwargs):
        c = self.get_object()
        another_contests = Contest.objects.filter(show=True, status='archived', published_dt__lte=timezone.now())
        if c:
            another_contests = another_contests.exclude(id=c.id)
        context = {
            'contest': c,
            'another_contests': another_contests,
        }
        context.update(super(ContestsHomeView, self).get_context_data(**kwargs))
        return context


class ContestDetailView(ContestsHomeView):
    template_name = 'contests/contest.html'

    def get_object(self, *args, **kwargs):
        kw = {'show': True, 'published_dt__lte': timezone.now()}
        contest = get_object_from_slug_and_kwargs(self.request, model=Contest, slug=self.kwargs.get('slug'), **kw)
        return contest


class ParticipantDetailView(DetailView):
    template_name = 'contests/participant.html'
    model = Participant
    context_object_name = 'participant'

    def get_object(self):
        kw = {'show': True, 'published_dt__lte': timezone.now()}
        self.contest = get_object_from_slug_and_kwargs(self.request, model=Contest, slug=self.kwargs.get('contest_slug'), **kw)
        participant = get_object_or_404(Participant, contest_id=self.contest.id, pk=self.kwargs.get('pk'))
        return participant

    def get_context_data(self, **kwargs):
        context = {
            'contest': self.contest,
        }
        context.update(super(ParticipantDetailView, self).get_context_data(**kwargs))
        return context


class ApplyView(GetNotAllowedMixin, JSONFormMixin, CreateView):
    form_class = ContestApplyForm
    mapping = {
        'contest': 'contest',
        'name': 'name',
        'description': 'description',
        'profile': 'profile',
        'photos': 'photos',
    }
    model = Participant

    def get_success_url(self):
        return self.request.path

    def get_object(self):
        return None

    def get_form(self, *args, **kwargs):
        profile = self.request.user
        if profile.is_anonymous():
            raise HttpResponseForbidden

        self.POST['profile'] = profile.id

        if hasattr(self, 'get_object'):
            form = self.form_class(self.POST, instance=self.get_object())
        else:
            form = self.form_class(self.POST)
        return form

    def form_valid(self, form):
        super(ApplyView, self).form_valid(form)
        participant = form.instance

        photos = [path for path in self.POST.get('photos', '').split(';') if path]
        for i, photo_path in enumerate(photos):
            try:
                if i == 0:
                    participant.photo.save(photo_path.split('/')[-1], File(open(photo_path[1:], 'rb')))
                    participant.save()

                photo = ParticipantPhoto.objects.create(participant=participant)
                photo.photo.save(photo_path.split('/')[-1], File(open(photo_path[1:], 'rb')))
                photo.save()
            except:
                pass

        if not participant.photo or not participant.photos.count():
            participant.delete()
            data = {'result': 'error', 'errors': [{'name': 'photos', 'label': 'Фото', 'error_message': 'Обязательное поле'}]}
            return JsonResponse(data, status=400)

        participant = form.instance
        return JsonResponse({'result': 'ok', 'redirect_url': participant.get_absolute_url()})


class AddLikeView(View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            try:
                DATA = json.loads(request.body)
                participant_id = DATA['id']
                participant = get_object_or_404(Participant, id=participant_id)
                liked_participants = request.session.get('liked_participants', [])

                participant_id = str(participant_id)
                if not participant_id in liked_participants:
                    participant.likes += 1
                    participant.save()
                    liked_participants.append(participant_id)
                    request.session['liked_participants'] = liked_participants

                return JsonResponse({'result': 'ok', 'count': participant.likes_count})

            except (ValueError, KeyError, Participant.DoesNotExist) as e:
                err_message = '{}: {}'.format(type(e).__name__, e.message)
                return JsonResponse({'result': 'error', 'count': None, 'error': err_message}, status=400)
        else:
            raise Http404


class RemoveLikeView(View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            try:
                DATA = json.loads(request.body)
                participant_id = DATA['id']
                participant = get_object_or_404(Participant, id=participant_id)
                liked_participants = request.session.get('liked_participants', [])

                participant_id = str(participant_id)
                if participant_id in liked_participants:
                    participant.likes -= 1
                    participant.save()
                    liked_participants.pop(liked_participants.index(participant_id))
                    request.session['liked_participants'] = liked_participants

                return JsonResponse({'result': 'ok', 'count': participant.likes_count})

            except (ValueError, KeyError, Participant.DoesNotExist) as e:
                err_message = '{}: {}'.format(type(e).__name__, e.message)
                return JsonResponse({'result': 'error', 'count': None, 'error': err_message}, status=400)
        else:
            raise Http404
