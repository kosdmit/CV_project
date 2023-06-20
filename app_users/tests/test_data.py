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