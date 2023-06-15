from urllib.parse import urlparse, urlunparse

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponseRedirect

from CV_project.settings import RATING_SETTINGS
from app_resume.models import Resume, WorkExpSection
from app_social.mixins import get_resume_by_element_uuid


class UserValidatorMixin:
    def form_valid(self, form):
        if self.request.user != self.object.user:
            raise PermissionDenied()

        return super().form_valid(form)


class ResumeValidatorMixin:
    def form_valid(self, form):
        users_resumes = self.request.user.resume_set.all()
        for resume in users_resumes:
            if resume == self.object.resume:
                return super().form_valid(form)
        raise PermissionDenied()


class WorkExpSectionValidatorMixin:
    def form_valid(self, form):
        try:
            self.object = form.save(commit=False)
        except AttributeError:
            pass

        try:
            work_exp_section = WorkExpSection.objects.get(resume__user=self.request.user,
                                                          pk=self.kwargs['section'])
            self.object.work_exp_section = work_exp_section
        except ObjectDoesNotExist:
            raise PermissionDenied

        return super().form_valid(form)


class RefreshIfSuccessMixin:
    def get_success_url(self):
        url = self.request.META['HTTP_REFERER']
        return remove_parameters_from_url(url, 'modal_id')


class ResumeBounderMixin:
    def form_valid(self, form):
        self.object = form.save(commit=False)
        try:
            resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        except Resume.DoesNotExist:
            raise PermissionDenied
        self.object.resume = resume

        return super().form_valid(form)


def remove_parameters_from_url(url, *args):
    parsed_url = urlparse(url)
    cleaned_query = ''

    parsed_query = parsed_url.query
    if parsed_query:
        params_to_remove = [*args]
        query_params = parsed_query.split('&')
        query_params = [param for param in query_params if param.split('=')[0] not in params_to_remove]
        cleaned_query = '&'.join(query_params)

    # Создаем новый URL-адрес без параметров
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, cleaned_query, parsed_url.fragment))

    return cleaned_url


class OpenModalIfSuccessMixin:
    def get_success_url(self):
        previous_url = self.request.META['HTTP_REFERER']
        cleaned_url = remove_parameters_from_url(previous_url, 'modal_id')

        return cleaned_url + '?modal_id=' + str(self.object.pk)


class RatingUpdateForCreateViewMixin:
    def form_valid(self, form):
        self.object.save()
        resume = get_resume_by_element_uuid(self.object.pk)
        resume.rating += RATING_SETTINGS['content']
        resume.save()

        return HttpResponseRedirect(self.get_success_url())


class RatingUpdateForDeleteViewMixin:
    def form_valid(self, form):
        resume = get_resume_by_element_uuid(self.object.pk)
        resume.rating -= RATING_SETTINGS['content']
        resume.save()

        return super().form_valid(form)


class GetResumeObjMixin:
    def get_object(self):
        user = User.objects.get(username=self.kwargs['username'])
        obj = Resume.objects.get(slug=self.kwargs['slug'], user=user)
        return obj
