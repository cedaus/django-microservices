import logging
import re
import pytz
import datetime
# DJANGO
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.contrib.auth.models import User
# PROJECT
from . import constants

logger = logging.getLogger('application')


def get_user(username):
    try:
        user = User.objects.get(username=username)
        return user
    except ObjectDoesNotExist:
        raise_error('ERR-USER-001')


def get_value_or_404(dict_, key):
    try:
        return dict_[key]
    except Exception as e:
        logger.error('Get value from dict error: ' + str(e))
        raise Http404(str(e))


def get_value_or_default(dict_, key, default=None):
    try:
        ret = dict_[key]
    except:
        ret = default
    return ret


def log_error(text):
    logger.error(text)


def get_error_text(code):
    if code:
        return constants.ERROR_CONFIG[code][0]


def raise_error(code=None, text=None):
    if code:
        error_text = constants.ERROR_CONFIG[code][0]
        logger.error(error_text)
        raise ValueError(error_text)
    elif text:
        logger.error(text)
        raise ValueError(text)


def create_response_obj(status, message=None, code=None, data=None):
    if status == 'success':
        val = 1
        success = True
        code = '201'
    elif status == 'error':
        val = 0
        success = False
    resp = {'value': val, 'success': success, 'status': status, 'message': message, 'code': code, 'data': data}
    return resp


def success_resp(data, message=None):
    return create_response_obj(status='success', message=message, data=data)


def error_resp(message, data=None):
    return create_response_obj(status='error', message=message, data=data)


def create_error_object(message, code=None):
    errors = []
    error = {'status': None, 'code': code, 'message': None, 'extra_data': None}
    error['message'] = message
    errors.append(error)
    return errors


def python_btoa(string):
    import base64
    string_byte = string.encode("utf-8")
    encoded_byte = base64.b64encode(string_byte)
    encoded_string = encoded_byte.decode("utf-8")
    return encoded_string


def validate_email(email):
    if email is None:
        return False
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    return True

def validate_phone(phone):
    if phone is None:
        return False
    if phone[:1] == '+' and phone[1:].isdigit():
        return True
    elif phone.isdigit():
        return True
    return False


def validate_get_phone(phone):


    phone_number = None
    phone_code = None
    if not validate_phone(phone):
        raise_error('ERR-GNRL-001')
    elif len(phone) < 10:
        raise_error('ERR-GNRL-001')
    elif phone[0] != '+' and len(phone) == 10:
        phone_number = phone
        phone_code = '91'
    elif phone[0] == '0' and len(phone) == 11:
        phone_number = phone[1:]
        phone_code = '91'
    elif phone[:2] == '91' and len(phone) == 12:
        phone_number = phone[2:]
        phone_code = phone[:2]
    elif phone[:3] == '+91' and len(phone) == 13:
        phone_number = phone[3:]
        phone_code = phone[1:3]
    elif not phone_number or not phone_code:
        raise_error('ERR-GNRL-001')
    data = {'phone_number': phone_number, 'phone_code': phone_code}
    return data

def get_phone_or_null(phone):
    phone_number = None
    phone_code = None
    if not validate_phone(phone):
        return None
    elif len(phone) < 10:
        return None
    elif phone[0] != '+' and len(phone) == 10:
        phone_number = phone
        phone_code = '91'
    elif phone[0] == '0' and len(phone) == 11:
        phone_number = phone[1:]
        phone_code = '91'
    elif phone[:2] == '91' and len(phone) == 12:
        phone_number = phone[2:]
        phone_code = phone[:2]
    elif phone[:3] == '+91' and len(phone) == 13:
        phone_number = phone[3:]
        phone_code = phone[1:3]
    elif not phone_number or not phone_code:
        return None

    data = {'phone_number': phone_number, 'phone_code': phone_code}
    return data



def random_with_N_digits(n):
    from random import randint
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def to_bool(val):
    if val is None:
        return None
    elif val is True or val is False:
        return val
    elif val.lower() == 'true':
        return True
    elif val.lower() == 'false':
        return False
    else:
        return None

"""
DATETIME
"""

def get_datetime(date):
    import datetime
    arr = date.split('-')
    return datetime.datetime(year=int(arr[0]), month=int(arr[1]), day=int(arr[2]))


def get_datetime_str(date):
    return '{}-{}-{}'.format(date.year, f"{date:%m}", f"{date:%d}")


def create_datetime(year, month, day, timezone=None):
    if timezone:
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.utc

    date_time = tz.localize(datetime.datetime(year, month, day))
    return date_time


def create_datetime_from_iso(datetime_str, timezone=None):
    if datetime_str is None or datetime_str is '':
        return None
    if timezone:
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.utc

    date_time = tz.localize(datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ'), is_dst=None)
    return date_time


def create_datetime_from_str(datetime_str, format, timezone=None):
    """
    '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z',
    :param datetime_str:
    :param timezone:
    :return:
    """
    if timezone:
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.utc

    date_time = tz.localize(datetime.datetime.strptime(datetime_str, format), is_dst=None)
    return date_time


def current_datetime(timezone=None):
    if timezone:
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.utc

    date_time = datetime.datetime.now(tz)
    return date_time


def yesterday_datetime(timezone=None):
    now = datetime.datetime.now()
    return create_datetime(now.year, now.month, now.day, timezone=timezone) - datetime.timedelta(days=1)


def today_datetime(timezone=None):
    now = datetime.datetime.now()
    return create_datetime(now.year, now.month, now.day, timezone=timezone)


def tomorrow_datetime(timezone=None):
    now = datetime.datetime.now()
    return create_datetime(now.year, now.month, now.day, timezone=timezone) + datetime.timedelta(days=1)


def week_datetime(timezone=None):
    now = datetime.datetime.now()
    start = now - datetime.timedelta(days=now.weekday())
    return create_datetime(start.year, start.month, start.day, timezone=timezone)


def week_end_datetime(timezone=None):
    now = datetime.datetime.now()
    num = 6 - now.weekday()
    start = now + datetime.timedelta(days=num)
    return create_datetime(start.year, start.month, start.day, timezone=timezone)


def timediff_hrs(start, end):
    x = (end - start)
    x = x.total_seconds() / 3600
    return x


def utc_to_user_datetime(date_time, timezone):
    """
    Converts the datetime obj from User Timezone to UTC
    :param date_time: aware_utc_dt_obj
    :param timezone: user timezone
    :return:
    """
    return date_time.astimezone(pytz.timezone(timezone))


def stringify_utc_to_user_datetime(date_time, timezone):
    """
    :param date_time:
    :param timezone:
    :return:
    """
    return date_time.astimezone(pytz.timezone(timezone)).strftime("%Y-%m-%dT%H:%M:%S")


def user_to_utc_datetime(date_time):
    """
    Converts the datetime obj from UTC to User Timezone
    :param date_time: aware_user_timezone_dt_obj
    :return:
    """
    return date_time.astimezone(pytz.utc)


def stringify_user_to_utc_datetime(date_time):
    """
    :param date_time:
    :param timezone:
    :return:
    """
    return date_time.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S")


def strp_to_user_datetime(datetime_str, timezone):
    unaware = datetime.datetime.strptime(datetime_str[:19], "%Y-%m-%dT%H:%M:%S")
    tz_obj = pytz.timezone(timezone)
    return tz_obj.localize(unaware)


def strp_to_utc_datetime(datetime_str, timezone=None):
    unaware = datetime.datetime.strptime(datetime_str[:19], "%Y-%m-%dT%H:%M:%S")
    if timezone:
        datetime_in_timezone = pytz.timezone(timezone).localize(unaware)
        datetime_in_utc = datetime_in_timezone.astimezone(pytz.utc)
    else:
        datetime_in_utc = pytz.utc.localize(unaware)
    return datetime_in_utc
