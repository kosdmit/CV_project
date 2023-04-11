from django.core.exceptions import ValidationError
from django.urls import reverse_lazy


class ResumeUpdateMixin:
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