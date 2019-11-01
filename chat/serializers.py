from rest_framework import serializers
from users.serializers import UserMiniSerializer
from . import models


class ChatMiniSerializer(serializers.ModelSerializer):
    participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    def get_participant(self, obj):
        try:
            user = self.context['user']
            if not user.is_anonymous():
                if user == obj.user1:
                    return UserMiniSerializer(obj.user2).data
                elif user == obj.user2:
                    return UserMiniSerializer(obj.user1).data
            else:
                return None
        except KeyError:
            return None

    def get_last_message(self, obj):
        return MessageSerializer(obj.get_last_message()).data

    class Meta:
        model = models.Chat
        exclude = []


class ChatSerializer(serializers.ModelSerializer):
    user1 = serializers.SerializerMethodField()
    user2 = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()
    total_messages_count = serializers.SerializerMethodField()

    def get_user1(self, obj):
        return UserMiniSerializer(obj.user1).data

    def get_user2(self, obj):
        return UserMiniSerializer(obj.user2).data

    def get_messages(self, obj):
        data = obj.get_messages()
        messages = MessageSerializer(data['messages'], many=True).data
        return messages

    def get_total_messages_count(self, obj):
        return obj.get_messages_count()

    class Meta:
        model = models.Chat
        exclude = []


class MessageSerializer(serializers.ModelSerializer):
    reference_content = serializers.SerializerMethodField()
    reference_user = serializers.SerializerMethodField()

    def get_reference_content(self, obj):
        return None

    def get_reference_user(self, obj):
        return None

    class Meta:
        model = models.Message
        exclude = []