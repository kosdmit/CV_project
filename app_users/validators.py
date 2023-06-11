import phonenumbers
from django.core.exceptions import ValidationError
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type, NumberParseException


def phone_number_validator(value):
    message = 'Введите корректный номер телефона'
    code = 'Incorrect phone number'
    number = value
    try:
        carrier._is_mobile(number_type(phonenumbers.parse(number)))
    except NumberParseException:
        raise ValidationError(message, code=code)