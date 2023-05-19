from django.urls import path

from app_job_hunt.views import RawContactEmployerCreateView

urlpatterns = [
    path('add_raw_contact', RawContactEmployerCreateView.as_view(), name='add_raw_contact'),

]