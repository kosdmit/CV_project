from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import OperationalError
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, RedirectView, DeleteView

from app_resume.forms import ResumeSoftSkillsForm, \
    MainEducationForm, \
    AdditionalEducationForm, ElectronicCertificateForm, InstitutionForm, \
    SkillCreateForm, \
    WorkExpSectionForm, JobForm, \
    ResumePositionForm, ResumeAboutMeForm
from app_resume.mixins import ResumeBounderMixin, OpenModalIfSuccessMixin, \
    RatingUpdateForCreateViewMixin, \
    RatingUpdateForDeleteViewMixin, UserValidatorMixin, RefreshIfSuccessMixin, \
    ResumeValidatorMixin, \
    WorkExpSectionValidatorMixin, GetResumeObjMixin, \
    remove_parameters_from_url, AddErrorMessagesToFormMixin, \
    Http404IfGetRequestMixin
from app_resume.models import Resume, MainEducation, Institution, AdditionalEducation, \
    ElectronicCertificate, Skill, WorkExpSection, Job

from app_social.forms import CommentForm, CommentUpdateForm, PostCreateForm, PostForm
from app_social.mixins import AddLikesIntoContextMixin
from app_social.models import Comment
from app_users.forms import SocialLinksForm


# Create your views here.
class MainView(RedirectView):
    USER_TO_REDIRECT = 'kosdmit'

    def get_redirect_url(self, *args, **kwargs):
        try:
            Resume.objects.get(user__username=self.USER_TO_REDIRECT, is_primary=True)
            url = reverse_lazy('primary_resume', kwargs={'username': self.USER_TO_REDIRECT})
        except Resume.MultipleObjectsReturned:
            url = reverse_lazy('primary_resume', kwargs={'username': self.USER_TO_REDIRECT})
        except (Resume.DoesNotExist, OperationalError):
            url = reverse_lazy('login')

        url_params = self.request.GET.urlencode()
        if url_params:
            url += '?' + self.request.GET.urlencode()

        return url


class ResumeView(AddLikesIntoContextMixin, TemplateView):
    template_name = 'app_resume/resume.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            owner = User.objects.get(username=kwargs['username'])
            context['owner'] = owner
        except User.DoesNotExist:
            raise Http404

        try:
            slug = kwargs['slug']
            resume = Resume.objects.get(slug=slug, profile=owner.profile)
        except KeyError:
            resume = Resume.objects.get(profile=owner.profile, is_primary=True)
        except Resume.DoesNotExist:
            raise Http404
        context['resume'] = resume

        context['post_set'] = resume.post_set.order_by('-created_date')[:2]

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

        for post in resume.post_set.all():
            uuid_list.append(post.pk)

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

        if self.request.user == owner:
            profile_url = '/users/profile/'
        else:
            profile_url = None

        breadcrumbs = [
            (owner.username, profile_url),
            (resume.position, reverse_lazy('resume', kwargs={'username': owner.username,
                                                             'slug': resume.slug})),
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
            'skill_create_form': SkillCreateForm(),
            'post_create_form': PostCreateForm(),
        }

        context.update(owners_forms)

        if main_education:
            context['institution_forms'] = {}
            for institution in resume.maineducation.institution_set.all():
                institution_form = InstitutionForm(instance=institution)
                context['institution_forms'][institution] = institution_form

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

        context['post_update_forms'] = {}
        for post in resume.post_set.all():
            post_update_form = PostForm(instance=post, auto_id=False)
            context['post_update_forms'][post] = post_update_form

        return context


class ResumeUpdateView(UserValidatorMixin,
                       GetResumeObjMixin,
                       RefreshIfSuccessMixin,
                       Http404IfGetRequestMixin,
                       UpdateView):
    model = Resume
    fields = ['position', 'about_me', 'soft_skills']

    def get_form_class(self):
        if 'position' in self.request.POST:
            form_class = ResumePositionForm
        elif 'about_me' in self.request.POST:
            form_class = ResumeAboutMeForm
        elif 'soft_skills' in self.request.POST:
            form_class = ResumeSoftSkillsForm

        return form_class

    def form_invalid(self, form):
        for error in form.errors:
            messages.warning(self.request,
                             f"{error}: {form.errors[error]}",
                             extra_tags='resume_update')

        if 'position' in self.request.POST:
            field_name = 'position'
        elif 'about_me' in self.request.POST:
            field_name = 'about_me'
        elif 'soft_skills' in self.request.POST:
            field_name = 'soft_skills'
        else:
            raise Http404

        return HttpResponseRedirect(
            remove_parameters_from_url(self.request.META['HTTP_REFERER'], 'modal_id')
            + f'?modal_id={field_name}-update-'
            + str(self.object.pk)
        )


class ResumeIsPrimaryUpdateView(UserValidatorMixin,
                                RefreshIfSuccessMixin,
                                Http404IfGetRequestMixin,
                                UpdateView):
    model = Resume
    fields = ['is_primary']

    def get_object(self, queryset=None):
        try:
            obj = Resume.objects.get(pk=self.request.POST['is_primary'])
        except ValidationError:
            raise Http404()
        return obj


class MainEducationCreateView(OpenModalIfSuccessMixin,
                              ResumeBounderMixin,
                              ResumeValidatorMixin,
                              RefreshIfSuccessMixin,
                              RatingUpdateForCreateViewMixin,
                              Http404IfGetRequestMixin,
                              CreateView):
    form_class = MainEducationForm


class MainEducationUpdateView(ResumeValidatorMixin,
                              RefreshIfSuccessMixin,
                              Http404IfGetRequestMixin,
                              UpdateView):
    form_class = MainEducationForm
    model = MainEducation


class InstitutionCreateView(OpenModalIfSuccessMixin,
                            ResumeBounderMixin,
                            ResumeValidatorMixin,
                            RefreshIfSuccessMixin,
                            RatingUpdateForCreateViewMixin,
                            Http404IfGetRequestMixin,
                            CreateView):
    model = Institution
    fields = ['title']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        try:
            resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        except Resume.DoesNotExist:
            raise PermissionDenied

        self.object.main_education = resume.maineducation

        return super().form_valid(form)


class InstitutionUpdateView(ResumeValidatorMixin,
                            RefreshIfSuccessMixin,
                            AddErrorMessagesToFormMixin,
                            Http404IfGetRequestMixin,
                            UpdateView):
    model = Institution
    fields = ['title', 'description', 'website_url', 'diploma', 'completion_date',
              'is_primary']
    url_name = 'institution_update'


class InstitutionDeleteView(ResumeValidatorMixin,
                            RefreshIfSuccessMixin,
                            RatingUpdateForDeleteViewMixin,
                            Http404IfGetRequestMixin,
                            DeleteView):
    model = Institution


class AdditionalEducationCreateView(OpenModalIfSuccessMixin,
                                    ResumeBounderMixin,
                                    ResumeValidatorMixin,
                                    RefreshIfSuccessMixin,
                                    RatingUpdateForCreateViewMixin,
                                    Http404IfGetRequestMixin,
                                    CreateView):
    model = AdditionalEducation
    fields = ['title']


class AdditionalEducationDeleteView(ResumeValidatorMixin,
                                    RatingUpdateForDeleteViewMixin,
                                    RefreshIfSuccessMixin,
                                    Http404IfGetRequestMixin,
                                    DeleteView):
    model = AdditionalEducation


class AdditionalEducationUpdateView(ResumeValidatorMixin,
                                    RefreshIfSuccessMixin,
                                    AddErrorMessagesToFormMixin,
                                    Http404IfGetRequestMixin,
                                    UpdateView):
    model = AdditionalEducation
    fields = ['title', 'description', 'website_url', 'diploma', 'completion_date']
    url_name = 'additional_education_update'


class ElectronicCertificateCreateView(OpenModalIfSuccessMixin,
                                      ResumeBounderMixin,
                                      ResumeValidatorMixin,
                                      RefreshIfSuccessMixin,
                                      RatingUpdateForCreateViewMixin,
                                      Http404IfGetRequestMixin,
                                      CreateView):
    model = ElectronicCertificate
    fields = ['title']


class ElectronicCertificateUpdateView(ResumeValidatorMixin,
                                      RefreshIfSuccessMixin,
                                      AddErrorMessagesToFormMixin,
                                      Http404IfGetRequestMixin,
                                      UpdateView):
    model = ElectronicCertificate
    fields = ['title', 'certificate_url', 'certificate', 'completion_percentage', 'completion_date']
    url_name = 'electronic_certificate_update'


class ElectronicCertificateDeleteView(ResumeValidatorMixin,
                                      RatingUpdateForDeleteViewMixin,
                                      RefreshIfSuccessMixin,
                                      Http404IfGetRequestMixin,
                                      DeleteView):
    model = ElectronicCertificate


class SkillCreateView(ResumeBounderMixin,
                      ResumeValidatorMixin,
                      RefreshIfSuccessMixin,
                      RatingUpdateForCreateViewMixin,
                      Http404IfGetRequestMixin,
                      CreateView):
    model = Skill
    fields = ['title']

    def form_invalid(self, form):
        for error in form.errors:
            messages.warning(self.request,
                             f"{error}: {form.errors[error]}",
                             extra_tags='skill_create')

        return HttpResponseRedirect(self.request.META['HTTP_REFERER'])


class SkillDeleteView(ResumeValidatorMixin,
                      RefreshIfSuccessMixin,
                      RatingUpdateForDeleteViewMixin,
                      Http404IfGetRequestMixin,
                      DeleteView):
    model = Skill


class WorkExpSectionCreateView(OpenModalIfSuccessMixin,
                               ResumeBounderMixin,
                               ResumeValidatorMixin,
                               RefreshIfSuccessMixin,
                               Http404IfGetRequestMixin,
                               CreateView):
    model = WorkExpSection
    fields = ['title']


class WorkExpSectionUpdateView(ResumeValidatorMixin,
                               RefreshIfSuccessMixin,
                               AddErrorMessagesToFormMixin,
                               Http404IfGetRequestMixin,
                               UpdateView):
    form_class = WorkExpSectionForm
    model = WorkExpSection
    url_name = 'work_exp_section_update'


class WorkExpSectionDeleteView(ResumeValidatorMixin,
                               RefreshIfSuccessMixin,
                               Http404IfGetRequestMixin,
                               DeleteView):
    model = WorkExpSection


class JobCreateView(OpenModalIfSuccessMixin,
                    WorkExpSectionValidatorMixin,
                    RefreshIfSuccessMixin,
                    RatingUpdateForCreateViewMixin,
                    Http404IfGetRequestMixin,
                    CreateView):
    model = Job
    fields = ['title']


class JobUpdateView(WorkExpSectionValidatorMixin,
                    RefreshIfSuccessMixin,
                    AddErrorMessagesToFormMixin,
                    Http404IfGetRequestMixin,
                    UpdateView):
    form_class = JobForm
    model = Job
    url_name = 'job_update'


class JobDeleteView(WorkExpSectionValidatorMixin,
                    RatingUpdateForDeleteViewMixin,
                    RefreshIfSuccessMixin,
                    Http404IfGetRequestMixin,
                    DeleteView):
    model = Job


