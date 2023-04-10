from django.urls import path

from app_resume.views import ResumeView


urlpatterns = [
    path('<username>/<slug>/', ResumeView.as_view(), name='resume'),

]