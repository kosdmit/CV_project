import os

from CV_project.settings import BASE_DIR

USERNAME = 'kosdmit'
PASSWORD = 'testpassword'

SIGNUP_CORRECT_DATA = {
    'username': 'newuser',
    'email': 'kosdmit@hotmail.com',
    'password1': 'testpassword',
    'password2': 'testpassword'
}

SIGNUP_INVALID_DATA = {
    'username': 'newuser',
    'email': 'kosdmit@hotmail.com',
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
    'first_name': 'dmitry',
    'last_name': 'kosyrkov',
    'email': 'kosdmit@hotmail.com'
}

USER_UPDATE_INVALID_DATA = {
    'username': 'invalid_username',
    'first_name': 'dmitry',
    'last_name': 'kosyrkov',
    'email': 'kosdmithotmail.com'
}

CREATE_PROFILE_CORRECT_DATA = {
    'birthday_date': '06.08.1993',
    'gender': 'F',
    'phone_number': '+79277535560',
    'image': os.path.join(BASE_DIR, 'media', 'avatars', '1.jpg')
}

CREATE_PROFILE_INVALID_DATA = {
    'birthday_date': '06.08.1993',
    'gender': 'F',
    'phone_number': '9277535560',
    'image': os.path.join(BASE_DIR, 'media', 'avatars', '1.jpg')
}

CREATE_RESUME_DATA = {
    'position': 'Python Developer'
}