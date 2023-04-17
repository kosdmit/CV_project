from django.urls import path

from app_resume.views import ResumeView, ResumeAboutMeUpdateView, ResumeSoftSkillsUpdateView, MainEducationCreateView, \
    AdditionalEducationCreateView, ElectronicCertificateCreateView, InstitutionCreateView, InstitutionUpdateView, \
    AdditionalEducationUpdateView, ElectronicCertificateUpdateView, SkillCreateView, WorkExpSectionCreateView, \
    JobCreateView, JobUpdateView

urlpatterns = [
    path('<username>/<slug>/', ResumeView.as_view(), name='resume'),
    path('<username>/<slug>/resume_about_me_update', ResumeAboutMeUpdateView.as_view(), name='resume_about_me_update'),
    path('<username>/<slug>/resume_soft_skills_update', ResumeSoftSkillsUpdateView.as_view(), name='resume_soft_skills_update'),
    path('<username>/<slug>/main_education_create', MainEducationCreateView.as_view(), name='main_education_create'),
    path('<username>/<slug>/institution_create', InstitutionCreateView.as_view(), name='institution_create'),
    path('<username>/<slug>/<pk>/institution_update/', InstitutionUpdateView.as_view(), name='institution_update'),
    path('<username>/<slug>/additional_education_create', AdditionalEducationCreateView.as_view(), name='additional_education_create'),
    path('<username>/<slug>/<pk>/additional_education_update/', AdditionalEducationUpdateView.as_view(), name='additional_education_update'),
    path('<username>/<slug>/electronic_certificate_create', ElectronicCertificateCreateView.as_view(), name='electronic_certificate_create'),
    path('<username>/<slug>/<pk>/electronic_certificate_update/', ElectronicCertificateUpdateView.as_view(), name='electronic_certificate_update'),
    path('<username>/<slug>/skill_create', SkillCreateView.as_view(), name='skill_create'),

    path('<username>/<slug>/work_exp_section_create', WorkExpSectionCreateView.as_view(), name='work_exp_section_create'),
    path('<username>/<slug>/<section>/job_create', JobCreateView.as_view(), name='job_create'),
    path('<username>/<slug>/<section>/<pk>/job_update', JobUpdateView.as_view(), name='job_update'),


]