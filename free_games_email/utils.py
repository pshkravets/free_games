from bcrypt import hashpw, gensalt


def email_validation(email):
    return email.endswith('@gmail.com')


def password_validation(passwd1, passwd2):
    return passwd1 == passwd2 and passwd1 is not None

def hash_password(password):
    return hashpw(bytes(password, 'utf-8'), gensalt()).decode('utf-8')
