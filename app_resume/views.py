from django.contrib.auth.models import User
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, RedirectView, DeleteView

from app_resume.forms import ResumeAboutMeForm, ResumeSoftSkillsForm, MainEducationForm, \
    AdditionalEducationForm, ElectronicCertificateForm, AdditionalEducationCreateForm, \
    ElectronicCertificateCreateForm, InstitutionCreateForm, InstitutionForm, SkillCreateForm, \
    WorkExpSectionForm, JobCreateForm, JobForm, ResumePositionForm
from app_resume.mixins import ResumeBounderMixin, OpenModalIfSuccessMixin, RatingUpdateForCreateViewMixin,\
    RatingUpdateForDeleteViewMixin, UserValidatorMixin, RefreshIfSuccessMixin, ResumeValidatorMixin, \
    WorkExpSectionValidatorMixin
from app_resume.models import Resume, MainEducation, Institution, AdditionalEducation, \
    ElectronicCertificate, Skill, WorkExpSection, Job

from app_social.forms import CommentForm, CommentUpdateForm
from app_social.mixins import AddLikesIntoContextMixin
from app_social.models import Comment
from app_users.forms import SocialLinksForm


# Create your views here.
class MainView(RedirectView):
    USER_TO_REDIRECT = 'kosdmit'

    try:
        Resume.objects.get(user__username=USER_TO_REDIRECT, is_primary=True)
        url_to_redirect = reverse_lazy('primary_resume', kwargs={'username': USER_TO_REDIRECT})
    except Resume.MultipleObjectsReturned:
        url_to_redirect = reverse_lazy('primary_resume', kwargs={'username': USER_TO_REDIRECT})
    except Resume.DoesNotExist:
        url_to_redirect = reverse_lazy('login')

    url = url_to_redirect


class ResumeView(AddLikesIntoContextMixin, TemplateView):
    template_name = 'app_resume/resume.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        owner = User.objects.get(username=kwargs['username'])
        context['owner'] = owner

        try:
            slug = kwargs['slug']
            resume = Resume.objects.get(slug=slug, profile=owner.profile)
        except KeyError:
            resume = Resume.objects.get(profile=owner.profile, is_primary=True)
        context['resume'] = resume

        try:
            main_education = resume.maineducation
        except MainEducation.DoesNotExist:
            main_education = None

        if self.request.user.is_authenticated and self.request.user == owner:
            context = self.add_owners_forms(context, owner, resume, main_education)

        uuid_list = []

        context['jobs_in_sections'] = {}
        for section in resume.workexpsection_set.all():
            jobs = Job.objects.filter(work_exp_section=section)
            job_form_dicts = []
            for job in jobs:
                uuid_list.append(job.pk)
                if self.request.user == owner:
                    job_update_form = JobForm(instance=job)
                    job_form_dicts.append({'job': job,
                                           'job_update_form': job_update_form})
                else:
                    job_form_dicts.append({'job': job})

            context['jobs_in_sections'][section] = job_form_dicts

        for institution in resume.institution_set.all():
            uuid_list.append(institution.pk)

        for additional_education in resume.additionaleducation_set.all():
            uuid_list.append(additional_education.pk)

        for electronic_certificate in resume.electroniccertificate_set.all():
            uuid_list.append(electronic_certificate.pk)

        for skill in resume.skill_set.all():
            uuid_list.append(skill.pk)

        for work_exp_section in resume.workexpsection_set.all():
            for job in work_exp_section.job_set.all():
                uuid_list.append(job.pk)

        comments = {}
        comment_edit_forms = {}
        for uuid_key in uuid_list:
            comments[uuid_key] = Comment.objects.filter(uuid_key=uuid_key, is_approved=True)
            for comment in comments[uuid_key]:
                if comment.owner_id == self.request.user or self.request.session.session_key:
                    comment_edit_forms[comment.pk] = CommentUpdateForm(
                        instance=comment)
        context['comments'] = comments
        context['comment_edit_forms'] = comment_edit_forms

        context['comment_form'] = CommentForm()

        comment_counts_result = Comment.objects.filter(is_approved=True) \
            .values('uuid_key') \
            .order_by('uuid_key') \
            .annotate(count=Count('uuid_key'))
        comment_counts = {}
        for dict in comment_counts_result:
            comment_counts[dict['uuid_key']] = dict['count']
        context['comment_counts'] = comment_counts

        breadcrumbs = [
            (owner.username, '/users/profile/'),
            (resume.position, ''),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context

    @staticmethod
    def add_owners_forms(context, owner, resume, main_education):
        owners_forms = {
            'resume_position_form': ResumePositionForm(instance=resume),
            'resume_about_me_form': ResumeAboutMeForm(instance=resume),
            'resume_soft_skills_form': ResumeSoftSkillsForm(instance=resume),
            'social_links_form': SocialLinksForm(instance=owner.profile.sociallinks),
            'main_education_form': MainEducationForm(instance=main_education),
            'additional_education_create_form': AdditionalEducationCreateForm(),
            'electronic_certificate_create_form': ElectronicCertificateCreateForm(),
            'skill_create_form': SkillCreateForm(),
            'work_exp_section_form': WorkExpSectionForm(),
            'job_create_form': JobCreateForm(),
        }

        context.update(owners_forms)

        if main_education:
            context['institution_forms'] = {}
            for institution in resume.maineducation.institution_set.all():
                institution_form = InstitutionForm(instance=institution)
                context['institution_forms'][institution] = institution_form

            context['institution_create_form'] = InstitutionCreateForm()

        context['additional_education_forms'] = {}
        for education in resume.additionaleducation_set.all():
            additional_education_form = AdditionalEducationForm(
                instance=education)
            context['additional_education_forms'][
                education] = additional_education_form

        context['electronic_certificate_forms'] = {}
        for certificate in resume.electroniccertificate_set.all():
            electronic_certificate_form = ElectronicCertificateForm(
                instance=certificate,
                auto_id=f"id_%s_{certificate.pk}"
            )
            context['electronic_certificate_forms'][
                certificate] = electronic_certificate_form

        context['work_exp_section_update_forms'] = {}
        for section in resume.workexpsection_set.all():
            work_exp_section_update_form = WorkExpSectionForm(
                instance=section,
                auto_id=f"id_%s_{section.pk}"
            )
            context['work_exp_section_update_forms'][
                section] = work_exp_section_update_form

        return context


class ResumePositionUpdateView(UserValidatorMixin, RefreshIfSuccessMixin, UpdateView):
    model = Resume
    fields = ['position']


class ResumeAboutMeUpdateView(UserValidatorMixin, RefreshIfSuccessMixin, UpdateView):
    model = Resume
    fields = ['about_me']


class ResumeSoftSkillsUpdateView(UserValidatorMixin, RefreshIfSuccessMixin, UpdateView):
    model = Resume
    fields = ['soft_skills']


class ResumeIsPrimaryUpdateView(UserValidatorMixin, RefreshIfSuccessMixin, UpdateView):
    model = Resume
    fields = ['is_primary']

    def get_object(self, queryset=None):
        obj = Resume.objects.get(pk=self.request.POST['is_primary'])
        return obj


class MainEducationCreateView(OpenModalIfSuccessMixin,
                              ResumeBounderMixin,
                              ResumeValidatorMixin,
                              RefreshIfSuccessMixin,
                              RatingUpdateForCreateViewMixin,
                              CreateView):
    form_class = MainEducationForm


class MainEducationUpdateView(ResumeValidatorMixin, RefreshIfSuccessMixin, UpdateView):
    form_class = MainEducationForm
    model = MainEducation


class InstitutionCreateView(OpenModalIfSuccessMixin,
                            ResumeBounderMixin,
                            ResumeValidatorMixin,
                            RefreshIfSuccessMixin,
                            RatingUpdateForCreateViewMixin,
                            CreateView):
    model = Institution
    fields = ['title']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        self.object.main_education = resume.maineducation

        return super().form_valid(form)


class InstitutionUpdateView(ResumeValidatorMixin,
                            RefreshIfSuccessMixin,
                            UpdateView):
    model = Institution
    fields = ['title', 'description', 'website_url', 'diploma', 'completion_date',
              'is_primary']


class InstitutionDeleteView(ResumeValidatorMixin,
                            RefreshIfSuccessMixin,
                            RatingUpdateForDeleteViewMixin,
                            DeleteView):
    model = Institution


class AdditionalEducationCreateView(OpenModalIfSuccessMixin,
                                    ResumeBounderMixin,
                                    ResumeValidatorMixin,
                                    RefreshIfSuccessMixin,
                                    RatingUpdateForCreateViewMixin,
                                    CreateView):
    model = AdditionalEducation
    fields = ['title']


class AdditionalEducationDeleteView(ResumeValidatorMixin,
                                    RatingUpdateForDeleteViewMixin,
                                    RefreshIfSuccessMixin,
                                    DeleteView):
    model = AdditionalEducation


class AdditionalEducationUpdateView(ResumeValidatorMixin,
                                    RefreshIfSuccessMixin,
                                    UpdateView):
    model = AdditionalEducation
    fields = ['title', 'description', 'website_url', 'diploma', 'completion_date']


class ElectronicCertificateCreateView(OpenModalIfSuccessMixin,
                                      ResumeBounderMixin,
                                      ResumeValidatorMixin,
                                      RefreshIfSuccessMixin,
                                      RatingUpdateForCreateViewMixin,
                                      CreateView):
    model = ElectronicCertificate
    fields = ['title']


class ElectronicCertificateUpdateView(ResumeValidatorMixin,
                                      RefreshIfSuccessMixin,
                                      UpdateView):
    model = ElectronicCertificate
    fields = ['title', 'certificate_url', 'certificate', 'completion_percentage', 'completion_date']


class ElectronicCertificateDeleteView(ResumeValidatorMixin,
                                      RatingUpdateForDeleteViewMixin,
                                      RefreshIfSuccessMixin,
                                      DeleteView):
    model = ElectronicCertificate


class SkillCreateView(ResumeBounderMixin,
                      ResumeValidatorMixin,
                      RefreshIfSuccessMixin,
                      RatingUpdateForCreateViewMixin,
                      CreateView):
    model = Skill
    fields = ['name']


class SkillDeleteView(ResumeValidatorMixin,
                      RefreshIfSuccessMixin,
                      RatingUpdateForDeleteViewMixin,
                      DeleteView):
    model = Skill


class WorkExpSectionCreateView(OpenModalIfSuccessMixin,
                               ResumeBounderMixin,
                               ResumeValidatorMixin,
                               RefreshIfSuccessMixin,
                               CreateView):
    form_class = WorkExpSectionForm


class WorkExpSectionUpdateView(ResumeValidatorMixin,
                               RefreshIfSuccessMixin,
                               UpdateView):
    form_class = WorkExpSectionForm
    model = WorkExpSection


class WorkExpSectionDeleteView(ResumeValidatorMixin,
                               RefreshIfSuccessMixin,
                               DeleteView):
    model = WorkExpSection


class JobCreateView(OpenModalIfSuccessMixin,
                    WorkExpSectionValidatorMixin,
                    RefreshIfSuccessMixin,
                    RatingUpdateForCreateViewMixin,
                    CreateView):
    model = Job
    fields = ['title']


class JobUpdateView(WorkExpSectionValidatorMixin,
                    RefreshIfSuccessMixin,
                    UpdateView):
    form_class = JobForm
    model = Job


class JobDeleteView(WorkExpSectionValidatorMixin,
                    RatingUpdateForDeleteViewMixin,
                    RefreshIfSuccessMixin,
                    DeleteView):
    model = Job


