from django.urls import path

from app_resume.views import ResumeView, MainEducationCreateView, \
    AdditionalEducationCreateView, ElectronicCertificateCreateView, \
    InstitutionCreateView, InstitutionUpdateView, \
    AdditionalEducationUpdateView, ElectronicCertificateUpdateView, \
    SkillCreateView, WorkExpSectionCreateView, \
    JobCreateView, JobUpdateView, ResumeIsPrimaryUpdateView, \
    InstitutionDeleteView, MainEducationUpdateView, \
    AdditionalEducationDeleteView, ElectronicCertificateDeleteView, \
    SkillDeleteView, WorkExpSectionUpdateView, \
    WorkExpSectionDeleteView, JobDeleteView, ResumeUpdateView

urlpatterns = [
    path('<username>/', ResumeView.as_view(), name='primary_resume'),
    path('<username>/<slug>/', ResumeView.as_view(), name='resume'),
    path('<username>/<slug>/resume_update', ResumeUpdateView.as_view(), name='resume_update'),
    path('<username>/resume_is_primary_update', ResumeIsPrimaryUpdateView.as_view(), name='resume_is_primary_update'),

    # Main education items
    path('<username>/<slug>/main_education_create', MainEducationCreateView.as_view(), name='main_education_create'),
    path('<username>/<slug>/<pk>/main_education_update', MainEducationUpdateView.as_view(), name='main_education_update'),
    path('<username>/<slug>/institution_create', InstitutionCreateView.as_view(), name='institution_create'),
    path('<username>/<slug>/<pk>/institution_update/', InstitutionUpdateView.as_view(), name='institution_update'),
    path('<username>/<slug>/<pk>/institution_delete/', InstitutionDeleteView.as_view(), name='institution_delete'),

    # Additional education items
    path('<username>/<slug>/additional_education_create', AdditionalEducationCreateView.as_view(), name='additional_education_create'),
    path('<username>/<slug>/<pk>/additional_education_update/', AdditionalEducationUpdateView.as_view(), name='additional_education_update'),
    path('<username>/<slug>/<pk>/additional_education_delete/', AdditionalEducationDeleteView.as_view(), name='additional_education_delete'),

    # Electronic certificate items
    path('<username>/<slug>/electronic_certificate_create', ElectronicCertificateCreateView.as_view(), name='electronic_certificate_create'),
    path('<username>/<slug>/<pk>/electronic_certificate_update/', ElectronicCertificateUpdateView.as_view(), name='electronic_certificate_update'),
    path('<username>/<slug>/<pk>/electronic_certificate_delete/', ElectronicCertificateDeleteView.as_view(), name='electronic_certificate_delete'),

    # Skill items
    path('<username>/<slug>/skill_create', SkillCreateView.as_view(), name='skill_create'),
    path('skill_delete/<pk>', SkillDeleteView.as_view(), name='skill_delete'),

    # Job items
    path('<username>/<slug>/work_exp_section_create', WorkExpSectionCreateView.as_view(), name='work_exp_section_create'),
    path('<username>/<slug>/<pk>/work_exp_section_update', WorkExpSectionUpdateView.as_view(), name='work_exp_section_update'),
    path('<username>/<slug>/<pk>/work_exp_section_delete', WorkExpSectionDeleteView.as_view(), name='work_exp_section_delete'),
    path('<username>/<slug>/<section>/job_create', JobCreateView.as_view(), name='job_create'),
    path('<username>/<slug>/<section>/<pk>/job_update', JobUpdateView.as_view(), name='job_update'),
    path('<username>/<slug>/<section>/<pk>/job_delete', JobDeleteView.as_view(), name='job_delete'),

]