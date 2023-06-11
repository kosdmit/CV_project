from django.core.exceptions import ValidationError
from django.test import TestCase

from app_resume.mixins import remove_parameters_from_url
from app_resume.validators import years_interval_validator, percentage_validator


# Create your tests here.

# Unit tests
class ValidatorsTests(TestCase):
    def test_years_interval_validator_with_correct_input(self):
        test_values = ['2000 - 2011', '2011 - 2015', '2015 - 2017']
        for value in test_values:
            years_interval_validator(value)

    def test_years_interval_validator_with_letters(self):
        test_values = ['200A - 2011', '2011 - 2015B', '20Q5 - AAAA']
        for value in test_values:
            with self.assertRaises(ValidationError):
                years_interval_validator(value)

    def test_years_interval_validator_with_lost_digits(self):
        test_values = ['200 - 2011', '2011 - 015', '205 - ']
        for value in test_values:
            with self.assertRaises(ValidationError):
                years_interval_validator(value)

    def test_years_interval_validator_with_lost_spaces(self):
        test_values = ['2000- 2011', '2011 -2015', '2015-2017']
        for value in test_values:
            with self.assertRaises(ValidationError):
                years_interval_validator(value)

    def test_percentage_validator_with_correct_input(self):
        test_values = [0, 10, 99, 100]
        for value in test_values:
            percentage_validator(value)

    def test_percentage_validator_with_negative_numbers(self):
        test_values = [-10, -99, -100]
        for value in test_values:
            with self.assertRaises(ValidationError):
                percentage_validator(value)

    def test_percentage_validator_with_big_numbers(self):
        test_values = [999, 1000]
        for value in test_values:
            with self.assertRaises(ValidationError):
                percentage_validator(value)

    def test_percentage_validator_with_float_numbers(self):
        test_values = [0.5, 10.1, 99.9, 100.0]
        for value in test_values:
            percentage_validator(value)


class FunctionTests(TestCase):
    def test_remove_parameters_from_url_with_correct_input(self):
        test_data = [
            {'url': 'http://127.0.0.1:8000/resume/kosdmit5/?modal_id=6cc12039-481f-4dd0-9202-d01e1943d9c0',
             'args': ['modal_id'],
             'expected': 'http://127.0.0.1:8000/resume/kosdmit5/'},

            {'url': 'http://127.0.0.1:8000/resume/kosdmit5/?modal_id=6cc12039-481f-4dd0-9202-d01e1943d9c0&id=007',
             'args': ['modal_id'],
             'expected': 'http://127.0.0.1:8000/resume/kosdmit5/?id=007'},

            {'url': 'http://127.0.0.1:8000/resume/kosdmit5/',
             'args': ['modal_id'],
             'expected': 'http://127.0.0.1:8000/resume/kosdmit5/'},
        ]

        for input_dict in test_data:
            self.assertEqual(remove_parameters_from_url(input_dict['url'],
                                                       *input_dict['args']),
                                                        input_dict['expected'])

