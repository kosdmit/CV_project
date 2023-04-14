from django.urls import path

from app_resume.views import ResumeView, ResumeAboutMeUpdateView, ResumeSoftSkillsUpdateView, MainEducationCreateView, \
    AdditionalEducationCreateView, ElectronicCertificateCreateView, InstitutionCreateView, InstitutionUpdateView

urlpatterns = [
    path('<username>/<slug>/', ResumeView.as_view(), name='resume'),
    path('<username>/<slug>/resume_about_me_update', ResumeAboutMeUpdateView.as_view(), name='resume_about_me_update'),
    path('<username>/<slug>/resume_soft_skills_update', ResumeSoftSkillsUpdateView.as_view(), name='resume_soft_skills_update'),
    path('<username>/<slug>/main_education_create', MainEducationCreateView.as_view(), name='main_education_create'),
    path('<username>/<slug>/institution_create', InstitutionCreateView.as_view(), name='institution_create'),
    path('<username>/<slug>/<pk>/institution_update/', InstitutionUpdateView.as_view(), name='institution_update'),
    path('<username>/<slug>/additional_education_create', AdditionalEducationCreateView.as_view(), name='additional_education_create'),
    path('<username>/<slug>/electronic_certificate_create', ElectronicCertificateCreateView.as_view(), name='electronic_certificate_create'),


]