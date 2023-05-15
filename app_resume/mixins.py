from urllib.parse import urlparse, urlunparse

from django.core.exceptions import ValidationError
from django.urls import reverse_lazy

from app_resume.models import Resume


class ResumeValidatorMixin:
    def form_valid(self, form):
        if not self.request.user.username == self.kwargs['username']:
            raise ValidationError(
                message='Username in URL is not correct',
                params={'your username': self.request.user.username,
                        'received username': self.kwargs['username'],
                        }
            )

        self.success_url = reverse_lazy('resume', kwargs={'username': self.kwargs['username'],
                                                          'slug': self.kwargs['slug'],
                                                          })
        super()
        return super().form_valid(form)


class ResumeBounderMixin:
    def form_valid(self, form):
        self.object = form.save(commit=False)
        resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        self.object.resume = resume

        super()
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
