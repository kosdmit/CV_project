from django.views.generic import CreateView

from app_job_hunt.forms import RawContactEmployerForm
from app_resume.mixins import RefreshIfSuccessMixin


# Create your views here.
class RawContactEmployerCreateView(RefreshIfSuccessMixin, CreateView):
    form_class = RawContactEmployerForm
