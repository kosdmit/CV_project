from django.views.generic import CreateView

from app_job_hunt.forms import RawContactEmployerForm
from app_resume.mixins import RefreshIfSuccessMixin, Http404IfGetRequestMixin


# Create your views here.
class RawContactEmployerCreateView(RefreshIfSuccessMixin,
                                   Http404IfGetRequestMixin,
                                   CreateView):
    form_class = RawContactEmployerForm
