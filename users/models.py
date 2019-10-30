# DJANGO
import uuid
from django.conf import settings
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db.models import Q

# PROJECT
from app import constants
from app.utils import raise_error, validate_email, random_with_N_digits, validate_get_phone, validate_phone, to_bool, \
                      get_datetime, get_user
from general.models import Phone
from general import firebase

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "authe.User")


class UserProfile(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, unique=True, on_delete=models.CASCADE)
    birth = models.DateField(null=True, blank=True)
    address_field = models.TextField(blank=True, null=True)
    sex = models.CharField(max_length=100, choices=constants.sex_choices, null=True, blank=True)
    phone_number = models.CharField(max_length=250, null=True, blank=True)
    phone_code = models.CharField(max_length=250, null=True, blank=True)
    phone_otp = models.CharField(max_length=6, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    read_notification_count = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    device_token = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "User Profile"

    def get_user_id(self):
        return self.user.id

    def get_username(self):
        return self.user.username

    def get_first_name(self):
        return self.user.first_name

    def get_last_name(self):
        return self.user.last_name

    def get_email(self):
        return self.user.email

    def get_name(self):
        name = ''
        first_name = self.get_first_name()
        last_name = self.get_last_name()
        if first_name:
            name = name + first_name
        if last_name:
            name = name + ' ' + last_name
        return name

    @classmethod
    def get_from_user(cls, user):
        try:
            obj = cls.objects.get(user=user)
        except ObjectDoesNotExist:
            raise_error(code='ERR-USER-001')
        return obj

    @staticmethod
    def get_random_username(first_name):
        uid = str(uuid.uuid4())[0:6]
        username = (first_name + uid).lower()
        try:
            User.objects.get(username=username)
            return UserProfile.get_random_username(first_name)
        except ObjectDoesNotExist:
            return username

    @staticmethod
    def match_user_from_email(email):
        if not validate_email(email):
            raise_error('ERR-GNRL-002')
        try:
            query = User.objects.get(email__iexact=email).userprofile
            return query
        except User.MultipleObjectsReturned:
            raise_error('ERR-DJNG-003')
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def match_user_from_username(username):
        try:
            query = UserProfile.objects.get(username__iexact=username)
            return query
        except User.MultipleObjectsReturned:
            raise_error('ERR-DJNG-003')
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def get_user_from_phone_number(phone_number, phone_code):
        try:
            query = UserProfile.objects.filter(phone_number=phone_number, phone_code=phone_code)
            return query.first()
        except ObjectDoesNotExist:
            return None

    @classmethod
    def create_with_phone(cls, phone_number, email, first_name, last_name, username=None, phone_otp=None):
        stored_phone = Phone.create(phone=phone_number)
        if phone_otp and (stored_phone.otp != phone_otp):
            raise_error('ERR-AUTH-005')
        user_profile = cls.create(email=email, first_name=first_name, last_name=last_name, username=username)
        user_profile.phone_number = stored_phone.number
        user_profile.phone_code = stored_phone.code
        user_profile.phone_otp = stored_phone.otp
        if phone_otp:
            user_profile.phone_verified = True
        user_profile.save()
        return user_profile

    @staticmethod
    def match_user_from_phone(phone):
        phone_data = validate_get_phone(phone)
        user_profile = UserProfile.get_user_from_phone_number(
            phone_number=phone_data['phone_number'], phone_code=phone_data['phone_code'])
        if not user_profile:
            Phone.create(phone)
        return user_profile

    @staticmethod
    def phone_input(operation, phone, OTP=None):
        if operation == 'VERIFY_USER_PHONE':
            user_profile = UserProfile.match_user_from_phone(phone)

            if not user_profile:
                raise_error('ERR-USER-001')
            if not OTP:
                raise_error('')
            if not user_profile.phone_otp:
                raise_error('ERR-USER-006')
            if not (user_profile.phone_otp == OTP):
                raise_error('ERR-AUTH-005')

            user_profile.phone_verified = True
            user_profile.save()
            verified = True
            data = {'phone_verified': verified}
            return data

        elif operation == 'VERIFY_USER_REGISTRATION':
            user_profile = UserProfile.match_user_from_phone(phone)
            if user_profile:
                data = {'user_registered': True}
            else:
                data = {'user_registered': False}

        elif operation == 'VERIFY_USER_REGISTRATION_SEND_OTP':
            user_profile = UserProfile.match_user_from_phone(phone)

            if user_profile:
                user_profile.set_phone_otp()
                # msg91_phone_otp_verification(phone=phone, OTP=user_profile.phone_otp)
            else:
                phone_obj = Phone.create(phone)
                # msg91_phone_otp_verification(phone=phone, OTP=phone_obj.otp)

            if user_profile:
                data = {'user_registered': True}
            else:
                data = {'user_registered': False}

        elif operation == 'SEND_PHONE_VERIFICATION_OTP_ALLOW_ANY':
            Phone.create(phone=phone, send_otp=True)
            return {'message': 'OTP Sent'}

        elif operation == 'SEND_PHONE_VERIFICATION_OTP':
            user_profile = UserProfile.match_user_from_phone(phone)
            if user_profile:
                user_profile.set_phone_otp()
                OTP = user_profile.phone_otp
                # data = msg91_phone_otp_verification(phone=phone, OTP=OTP)
            else:
                raise_error('ERR-USER-001')
        return data

    @classmethod
    def create(cls, email, first_name, last_name, username=None, phone=None):
        if phone and UserProfile.match_user_from_phone(phone):
            raise_error('ERR-USER-004')
        if UserProfile.match_user_from_email(email=email):
            raise_error('ERR-USER-005')
        if username and UserProfile.match_user_from_username(username):
            raise_error('ERR-USER-008')

        if username is None:
            username = UserProfile.get_random_username(first_name)

        user = User.objects.create(username=username, email=email, first_name=first_name, last_name=last_name)
        user_profile = cls.objects.create(user=user)
        firebase.setup_user_on_firebase(user)
        return user_profile