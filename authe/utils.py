import logging
# DJANGO
# PROJECT
from ois.utils import raise_error
from user.models import UserProfile
from . import jwt_utils

logger = logging.getLogger("application")


def create_user_from_phone(phone_number, username, email, first_name, last_name, password1, password2):
    if password1 != password2:
        raise_error('ERR-AUTH-004')

    user = UserProfile.create_with_phone(phone_number=phone_number, email=email, first_name=first_name,
                                         last_name=last_name, username=username).user
    user.set_password(password1)
    user.save()
    token = jwt_utils.get_token_for_user(user)
    data = {'username': user.username, 'token': token, 'user_id': user.id}
    return data


def get_user_from_phone(phone_number, password=None, phone_otp=None):

    if not password and not phone_otp:
        raise_error('ERR-AUTH-001')

    user_profile = UserProfile.match_user_from_phone(phone=phone_number)

    if user_profile is None:
        raise_error('ERR-USER-001')

    user = user_profile.user
    if password and user.check_password(password):
        token = jwt_utils.get_token_for_user(user)
        data = {'token': token, 'user_id': user.id, 'username': user.username}
        return data
    elif phone_otp and user_profile.phone_otp == phone_otp:
        token = jwt_utils.get_token_for_user(user)
        data = {'token': token, 'user_id': user.id, 'username': user.username}
        return data
    else:
        raise_error('ERR-AUTH-001')

