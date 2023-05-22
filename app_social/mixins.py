from urllib.parse import urlparse, urlunparse

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q

from app_resume.models import Resume
from app_social.models import Like


def remove_parameters_from_url(url, *args):
    parsed_url = urlparse(url)
    cleaned_query = ''

    parsed_query = parsed_url.query
    if parsed_query:
        params_to_remove = [*args]
        query_params = parsed_query.split('&')
        query_params = [param for param in query_params if param.split('=')[0] not in params_to_remove]
        cleaned_query = '&'.join(query_params)

    # Создаем новый URL-адрес без параметров
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, cleaned_query, parsed_url.fragment))

    return cleaned_url


class OpenCommentModalIfSuccess:
    def get_success_url(self):
        previous_url = self.request.META['HTTP_REFERER']
        cleaned_url = remove_parameters_from_url(previous_url, 'modal_id')

        return cleaned_url + '?modal_id=comments-' + str(self.object.uuid_key)


class AddLikesIntoContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            user_likes = Like.objects.filter(owner_id=self.request.user.id).all()
        else:
            session_id = self.request.session.session_key
            if not session_id:
                self.request.session.save()
                session_id = self.request.session.session_key
            user_likes = Like.objects.filter(owner_id=session_id).all()

        user_likes_uuid = []
        for like in user_likes:
            user_likes_uuid.append(like.uuid_key)
        context['users_likes_uuid'] = user_likes_uuid

        like_counts_result = Like.objects.values('uuid_key') \
            .order_by('uuid_key') \
            .annotate(count=Count('uuid_key'))
        like_counts = {}
        for dict in like_counts_result:
            like_counts[dict['uuid_key']] = dict['count']
        context['like_counts'] = like_counts

        return context


def get_resume_by_element_uuid(uuid):
    resume = Resume.objects.filter(
        Q(maineducation__pk=uuid) |
        Q(institution__pk=uuid) |
        Q(additionaleducation__pk=uuid) |
        Q(electroniccertificate__pk=uuid) |
        Q(skill__pk=uuid) |
        Q(workexpsection__job__pk=uuid) |
        Q(pk=uuid)
    ).distinct().first()

    return resume


class OwnerValidatorMixin:
    def form_valid(self, form):
        if self.request.user.is_authenticated and self.object.user == self.request.user \
                or self.object.owner_id == self.request.session.session_key:
            return super().form_valid(form)
        else:
            raise PermissionDenied