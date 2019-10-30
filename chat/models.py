import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q

from app import constants, settings
from app.utils import raise_error
from general.firebase import notify_new_msg_to_user, create_chat_on_firebase


class Chat(models.Model):
    user1 = models.ForeignKey(User, related_name='primary_user', null=False, blank=False)
    user2 = models.ForeignKey(User, related_name='secondary_user', null=False, blank=False)
    last_msg_read_by_user1 = models.BooleanField(default=True)
    last_msg_read_by_user2 = models.BooleanField(default=True)
    firebase_id = models.CharField(max_length=250, null=True, blank=True)
    started = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now_add=True, editable=True)

    class Meta:
        unique_together = ('user1', 'user2')
        get_latest_by = 'created'
        ordering = ['-created']
        verbose_name = 'Chat'

    @classmethod
    def get_obj(cls, id):
        try:
            obj = cls.objects.get(id=id)
        except ObjectDoesNotExist:
            raise ValueError('No object found')
        return obj

    @classmethod
    def get_for_user(cls, user, id):
        try:
            obj = cls.objects.get(Q(user1=user) | Q(user2=user), id=id)
        except ObjectDoesNotExist:
            raise ValueError('No object found')
        return obj

    def create_firebase_id(self):
        firebase_id = str(self.user1.id) + '_' + str(self.user2.id)
        create_chat_on_firebase(firebase_id=firebase_id, user1_id=self.user1.id, user2_id=self.user2.id)
        self.firebase_id = firebase_id
        self.save()

    @staticmethod
    def create_chat_with_member(user, member_id):
        if not user or not member_id:
            raise_error('ERR-CHAT-003')
        elif user.id == member_id:
            raise_error('ERR-CHAT-002')

        if user.id < member_id:
            user1 = user
            user2 = User.objects.get(id=member_id)
        else:
            user1 = User.objects.get(id=member_id)
            user2 = user

        try:
            chat = Chat.objects.get(Q(Q(user1=user1) & Q(user2=user2)) | Q(Q(user1=user2) & Q(user2=user1)))
        except ObjectDoesNotExist:
            chat = Chat.objects.create(user1=user1, user2=user2)
            chat.create_firebase_id()
        return chat

    @staticmethod
    def create(user1, user2):
        if not user1 or not user2:
            raise_error('ERR-CHAT-003')
        elif user1.username == user2.username:
            raise_error('ERR-CHAT-002')

        try:
            chat = Chat.objects.get(Q(Q(user1=user1) & Q(user2=user2)) | Q(Q(user1=user2) & Q(user2=user1)))
        except ObjectDoesNotExist:
            chat = Chat.objects.create(user1=user1, user2=user2)
            chat.create_firebase_id()
        return chat

    @staticmethod
    def get_chats(user, offset):
        limit = 10
        chats = Chat.objects.filter(Q(user1=user) | Q(user2=user), started=True).order_by('-modified')[
                offset:offset + limit]
        data = {'chats': chats, 'count': chats.count()}
        return data

    def get_messages_count(self):
        return Message.objects.filter(chat=self).count()

    def get_messages(self, offset=0):
        limit = 20
        messages = Message.objects.filter(chat=self).order_by('-created')[offset:offset + limit]
        data = {'messages': messages, 'count': messages.count()}
        return data

    @staticmethod
    def get_old_messages_for_chat(user, chat_id, offset):
        chat = Chat.get_for_user(user=user, id=chat_id)
        limit = 10
        messages = Message.objects.filter(chat=chat).order_by('-created')[int(offset):int(offset) + limit]
        data = {'messages': messages, 'count': messages.count()}
        return data

    @staticmethod
    def get_new_messages_for_chat(user, chat_id, offset):
        chat = Chat.get_for_user(user=user, id=chat_id)
        messages = Message.objects.filter(chat=chat)[int(offset):]
        total_messages_count = Message.objects.filter(chat=chat).count()
        data = {'messages': messages, 'count': messages.count(), 'total_messages_count': total_messages_count}
        return data

    @staticmethod
    def add_message(chat_id, from_user, message, reference_type=None, reference_id=None):
        from datetime import datetime
        chat = Chat.get_obj(id=chat_id)
        if not chat.active:
            raise_error('ERR-CHAT-001')
        msg_number = Message.objects.filter(chat=chat).count() + 1
        msg = Message.objects.create(chat=chat, from_user=from_user, text=message,
                                     message_number=msg_number)
        chat.modified = datetime.now()
        chat.save()
        if reference_type and reference_id:
            msg.reference_type = reference_type
            msg.reference_id = reference_id
            msg.save()
        if chat.started is False:
            chat.started = True
            chat.save()

        notify_new_msg_to_user(from_user=from_user, chat=chat, count=msg_number)
        data = {'message': msg}
        return data

    def get_last_message(self):
        last_message = Message.objects.filter(chat=self).last()
        return last_message


class Message(models.Model):
    class Meta:
        get_latest_by = "message_number"
        verbose_name = "Message"

    created = models.DateTimeField(auto_now_add=True, editable=False)
    from_user = models.ForeignKey(User, related_name='from_user', null=False, blank=False)
    type = models.CharField(choices=constants.chat_type_states_choices, max_length=30,
                            default=constants.chat_type_states['TEXT'])
    text = models.TextField(null=True, blank=True)
    file = models.ForeignKey('general.File', null=True, blank=True)
    file_name = models.TextField(null=True, blank=True)
    message_number = models.BigIntegerField(default=0)
    chat = models.ForeignKey(Chat, null=True)
    reference_type = models.CharField(choices=constants.reference_type_states_choices, max_length=500, null=True,
                                      blank=True)
    reference_id = models.CharField(max_length=500, null=True, blank=True)
    action = models.CharField(max_length=40, blank=True, null=True)
    action_params = models.TextField(blank=True, null=True)

    def get_type(self):
        return self.type

    def get_file_url(self):
        if self.file:
            return self.file.get_url()
        else:
            return ""

    def get_file_name(self):
        if self.file:
            return self.file.get_name()
        else:
            return ""

    def get_text(self):
        return self.text

    def get_message_action(self):
        return self.action

    def get_action_params(self):
        if self.action_params:
            return json.loads(self.action_params)
        else:
            return []
