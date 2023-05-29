from django import template

register = template.Library()


@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
    value = None
    if key:
        try:
            value = dict_data.get(key)
        except AttributeError:
            pass
        return value
