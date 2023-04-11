from django.urls import path

from app_resume.views import ResumeView, ResumeAboutMeUpdateView, ResumeSoftSkillsUpdateView

urlpatterns = [
    path('<username>/<slug>/', ResumeView.as_view(), name='resume'),
    path('<username>/<slug>/resume_about_me_update', ResumeAboutMeUpdateView.as_view(), name='resume_about_me_update'),
    path('<username>/<slug>/resume_soft_skills_update', ResumeSoftSkillsUpdateView.as_view(), name='resume_soft_skills_update'),

]