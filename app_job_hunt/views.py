from django.shortcuts import render
from django.views.generic import CreateView

from app_job_hunt.forms import RawContactEmployerForm


# Create your views here.
class RawContactEmployerCreateView(CreateView):
    form_class = RawContactEmployerForm

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']
