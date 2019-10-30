from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from app.utils import validate_get_phone, random_with_N_digits
# Create your models here.


class Phone(models.Model):
    number = models.CharField(max_length=250)
    code = models.CharField(max_length=250)
    otp = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    class Meta:
        unique_together = (('number', 'code'),)

    @staticmethod
    def create(phone):
        phone_data = validate_get_phone(phone)
        try:
            obj = Phone.objects.get(number=phone_data['phone_number'], code=phone_data['phone_code'])
        except ObjectDoesNotExist:
            obj = Phone.objects.create(number=phone_data['phone_number'],
                                       code=phone_data['phone_code'], otp=random_with_N_digits(4))
        return obj
