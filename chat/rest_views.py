from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from authe.jwt_utils import JWTAuthentication
from commune.utils import success_resp, error_resp, get_value_or_default, get_value_or_404
from . import models, serializers


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_chat_list(request):
    try:
        offset = int(get_value_or_default(request.GET, 'offset', 0))
        data = models.Chat.get_chats(user=request.user, offset=offset)
        chats = serializers.ChatMiniSerializer(data['chats'], many=True, context={'user': request.user}).data
        context = {'chats': chats, 'count': data['count']}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_chat(request, member_id):
    try:
        chat = serializers.ChatSerializer(models.Chat.create_chat_with_member(user=request.user, member_id=int(member_id))).data
        context = {'chat': chat}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_chat(request, chat_id):
    try:
        chat = serializers.ChatSerializer(models.Chat.get_for_user(user=request.user, id=chat_id)).data
        context = {'chat': chat}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_message(request, chat_id):
    try:
        message = get_value_or_404(request.data, 'message')
        reference_type = get_value_or_default(request.data, 'reference_type', None)
        reference_id = get_value_or_default(request.data, 'reference_id', None)
        data = models.Chat.add_message(chat_id=chat_id, from_user=request.user, message=message, reference_id=reference_id, reference_type=reference_type)
        message = serializers.MessageSerializer(data['message']).data
        print(message)
        context = {'message': message, 'total_messages_count': data['message'].message_number}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_new_message(request, chat_id):
    try:
        offset = get_value_or_404(request.GET, 'offset')
        data = models.Chat.get_new_messages_for_chat(user=request.user, chat_id=chat_id, offset=offset)
        messages = serializers.MessageSerializer(data['messages'], many=True).data
        context = {'messages': messages, 'total_messages_count': data['total_messages_count']}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_old_message(request, chat_id):
    try:
        offset = get_value_or_404(request.GET, 'offset')
        data = models.Chat.get_old_messages_for_chat(user=request.user, chat_id=chat_id, offset=offset)
        messages = serializers.MessageSerializer(data['messages'], many=True).data
        context = {'messages': messages}
        return Response(success_resp(data=context), status=status.HTTP_200_OK)
    except ValueError as ve:
        return Response(error_resp(message=str(ve)), status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(error_resp(message=str(e)), status=status.HTTP_400_BAD_REQUEST)