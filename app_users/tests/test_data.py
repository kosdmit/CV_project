import os

from CV_project.settings import BASE_DIR

USERNAME = 'kosdmit'
PASSWORD = 'testpassword'
EMAIL = 'kosdmit@hotmail.com'
FIRST_NAME = 'Dmitry'
LAST_NAME = 'Kosyrkov'
PHONE_NUMBER = '+79277535560'
BIRTHDAY_DATE = '06.08.1993'
POSITION = 'Python Developer'
VK_URL = 'https://vk.com/kosdmit/'
GITHUB_URL = 'https://github.com/kosdmit/'

SIGNUP_CORRECT_DATA = {
    'username': USERNAME,
    'email': EMAIL,
    'password1': PASSWORD,
    'password2': PASSWORD
}

SIGNUP_INVALID_DATA = {
    'username': USERNAME,
    'email': EMAIL,
    'password1': 't',
    'password2': 't'
}

LOGIN_CORRECT_DATA = {
    'username': USERNAME,
    'password': PASSWORD
}

LOGIN_INVALID_DATA = {
    'username': USERNAME,
    'password': 'wrongpassword'
}

USER_UPDATE_CORRECT_DATA = {
    'username': 'updated_username',
    'first_name': FIRST_NAME,
    'last_name': LAST_NAME,
    'email': EMAIL
}

USER_UPDATE_INVALID_DATA = {
    'username': 'invalid_username',
    'first_name': FIRST_NAME,
    'last_name': LAST_NAME,
    'email': 'kosdmithotmail.com'
}

CREATE_PROFILE_CORRECT_DATA = {
    'birthday_date': BIRTHDAY_DATE,
    'gender': 'F',
    'phone_number': PHONE_NUMBER,
    'image': os.path.join(BASE_DIR, 'media', 'avatars', '1.jpg')
}

CREATE_PROFILE_INVALID_DATA = {
    'birthday_date': BIRTHDAY_DATE,
    'gender': 'F',
    'phone_number': '9277535560',
    'image': os.path.join(BASE_DIR, 'media', 'avatars', '1.jpg')
}

CREATE_RESUME_DATA = {
    'position': POSITION
}