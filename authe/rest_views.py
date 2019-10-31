import logging
#
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
# Project
from ois.utils import get_value_or_404, get_value_or_default, create_error_object, success_resp, error_resp, \
    raise_error
from . import utils, jwt_utils

logger = logging.getLogger(__name__)


class PhoneAuth(APIView):
    permission_classes = (AllowAny,)

    def put(self, request, format=None):
        phone_number = get_value_or_404(request.data, 'phone_number')
        email = get_value_or_404(request.data, 'email')
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')
        first_name = get_value_or_default(request.data, 'first_name', None)
        last_name = get_value_or_default(request.data, 'last_name', None)
        username = get_value_or_default(request.data, 'username', None)

        try:
            context = utils.create_user_from_phone(phone_number=phone_number, username=username,
                                                   email=email, first_name=first_name,
                                                   last_name=last_name, password1=password1,
                                                   password2=password2)
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        phone_number = get_value_or_404(request.data, 'phone_number')
        password = get_value_or_default(request.data, 'password', None)
        phone_otp = get_value_or_default(request.data, 'phone_otp', None)

        try:
            context = utils.get_user_from_phone(phone_number=phone_number, password=password, phone_otp=phone_otp)
            return Response(success_resp(data=context), status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([jwt_utils.JWTAuthentication])
@permission_classes([IsAuthenticated])
def set_password(request):
    try:
        password1 = get_value_or_404(request.data, 'password1')
        password2 = get_value_or_404(request.data, 'password2')

        if password1 != password2:
            raise_error('ERR-AUTH-004')

        request.user.set_password(password1)
        request.user.save()
        context = {'message': 'Password successfully changed'}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([jwt_utils.JWTAuthentication])
@permission_classes([IsAuthenticated])
def reset_password(request):
    old_password = get_value_or_404(request.data, 'old_password')
    password1 = get_value_or_404(request.data, 'password1')
    password2 = get_value_or_404(request.data, 'password2')

    if not request.user.check_password(old_password):
        return Response('ERROR INCORRECT CURRENT PASSWORD', status=status.HTTP_400_BAD_REQUEST)

    if password1 != password2:
        return Response('ERROR PASSWORD DOES NOT MATCH', status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(password1)
    request.user.save()

    return Response({'message': 'PASSWORD CHANGED'}, status=status.HTTP_200_OK)
