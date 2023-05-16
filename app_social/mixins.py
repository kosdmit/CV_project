from urllib.parse import urlparse, urlunparse


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