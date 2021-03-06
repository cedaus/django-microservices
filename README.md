# django-microservices
This project is not an Introduction to Django. To get the most out of it, you should be familiar with Django.
This project comprises of following microservices/micro-features built on top of Django Framework

1. Real Time Chat
2. Celery and Redis based contacts upload
3. JWT Authentication with Phone, Email, Google, Facebook
4. Notification feed
5. Elastic Search based text and tag search engine

## REAL TIME CHAT
In this part I will talk about developing a real time chat. You can check the chat working in this video.
#### Features of Chat App:
* Chat is based on channel which comprise of two participants
* Participants can send each other messages in text, file and image formats
* Participants can take actions like delete and forward a message

#### Libraries Used:
* Firebase
* AWS S3

#### Development:
##### 1. Defining a django models
Our Chat architecture comprises of a Chat Model which is a channel between two participants. And Message Model which are messages sent across the Chat.

> Code snippet from chat/models.py
```
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
```

Each message object has an associated Foreignkey to Chat & User username, timestamp, and the actual message text.
> Code snippet from chat/models.py
```
class Message(models.Model):
    class Meta:
        get_latest_by = "message_number"
        verbose_name = "Message"

    created = models.DateTimeField(auto_now_add=True, editable=False)
    from_user = models.ForeignKey(User, related_name='from_user', null=False, blank=False)
    type = models.CharField(choices=constants.chat_type_states_choices, max_length=30,default=constants.chat_type_states['TEXT'])
    text = models.TextField(null=True, blank=True)
    file = models.ForeignKey('general.File', null=True, blank=True)
    file_name = models.TextField(null=True, blank=True)
    message_number = models.BigIntegerField(default=0)
    chat = models.ForeignKey(Chat, null=True)
    reference_type = models.CharField(choices=constants.reference_type_states_choices, max_length=500, null=True,blank=True)
    reference_id = models.CharField(max_length=500, null=True, blank=True)
    action = models.CharField(max_length=40, blank=True, null=True)
    action_params = models.TextField(blank=True, null=True)
```
##### 2. Putting Firebase endpoints
Before we dive into the the read and write operation to firebase, first of all create a model on firebase db that represent the scruture of chat message, such that our Chat collection on firebase looks like this

```
-chats
   - chatID
       - user1
       - user2
       - total_messages_count
       - last_message_timestamp
```
Here chatID (LowerUserId_HigherUserId) is the conversation node between User1 for ex: 108 and User2 for ex: 109 and is also set as firebase_id in Chat Model in Djnago

Our next step would be defining some write operations for Firebase.
> Code snippet from general/firebase.py
```
def create_chat_on_firebase(firebase_id, user1_id, user2_id):
    if get_from_environment('SETUP') == 'PRODUCTION':
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': firebase_app})
        db = firestore.client()
        context = {'notify_new_message_to_user1': False, 'notify_new_message_to_user2': False,'total_messages_count': 0, 'user1': user1_id, 'user2': user2_id}
        db.collection('chats').document(firebase_id).set(context)

```
> Code snippet from general/firebase.py
```
def notify_new_msg_to_user(from_user, chat, count):
    if get_from_environment('SETUP') == 'PRODUCTION':
        if not firebase_ins:
            firebase_admin.initialize_app(cred, {'projectId': firebase_app})
        db = firestore.client()
        if from_user == chat.user1 and chat.firebase_id:
            db.collection('chats').document(chat.firebase_id).set({'total_messages_count': count}, merge=True)
            db.collection(u'users-external-event').document(str(chat.user2.id)).set({'notify_new_message': True},merge=True)
            push_notification_trigger(to_user=chat.user2, from_user=from_user, type='NEW_MESSAGE',reference_id=chat.user1.id,reference_username=chat.user1.username)
        elif from_user == chat.user2 and chat.firebase_id:
            db.collection('chats').document(chat.firebase_id).set({'total_messages_count': count}, merge=True)
            db.collection(u'users-external-event').document(str(chat.user1.id)).set({'notify_new_message': True},merge=True)
            push_notification_trigger(to_user=chat.user1, from_user=from_user, type='NEW_MESSAGE',reference_id=chat.user2.id, reference_username=chat.user2.username)
```
##### 3. Writing REST APIs and defining endpoints

> Code snippet from chat/api_urls.py
```
urlpatterns = [
    url(r'^list/$', rest_views.get_chat_list),
    url(r'^create/(?P<member_id>[-\w\d]+)/$', rest_views.create_chat),
    url(r'^(?P<chat_id>[-\w\d]+)/$', rest_views.get_chat),
    url(r'^message/add/(?P<chat_id>[-\w\d]+)/', rest_views.add_message),
    url(r'^message/new/(?P<chat_id>[-\w\d]+)/', rest_views.get_new_message),
    url(r'message/old/(?P<chat_id>[-\w\d]+)/$', rest_views.get_old_message)
]
```

## CONTACTS AND INVITE BUILT WITH CELERY

#### Libraries used:
1. celery==4.2.2
2. redis==3.3.4

#### Development:
##### 1. Setup for Celery in Django

> Code snippet from app/celery.py
```
from __future__ import absolute_import
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery()

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

```

> Code snippet from app/settings.py
```
# -----------------------------
# REDIS
# -----------------------------
# redis_url = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379')
redis_url = get_from_environment('REDISCLOUD_URL')

# -----------------------------
# CELERY
# -----------------------------
CELERY_BROKER_URL = get_from_environment('REDISCLOUD_URL')
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'application/text']

CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERYD_MAX_TASKS_PER_CHILD = 1

CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
BROKER_POOL_LIMIT = 1  # Will decrease connection usage
BROKER_CONNECTION_TIMEOUT = 30  # May require a long timeout due to Linux DNS timeouts etc
BROKER_HEARTBEAT = 30  # Will detect stale connections faster
CELERY_SEND_EVENTS = False  # Will not create celeryev.* queues
CELERY_EVENT_QUEUE_EXPIRES = 86400 * 14  # Will delete all celeryev. queues without consumers after 1 minute.
DEFAULT_CACHE_EXPIRE = 60
```


##### 2. Defining Django Models
> Code snippet from contacts/models.py
```
class UserContact(models.Model):
    user = models.ForeignKey(User, db_index=True)
    contact = models.ForeignKey(User, null=True, related_name="user_contact")
    source = models.CharField(max_length=10, choices=constants.imported_contact_sources_choices)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, db_index=True, null=True)
    phone_code = models.CharField(max_length=5, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=10, choices=constants.user_contact_states_choices, default='0')
    block_invites = models.BooleanField(default=False)
    registered = models.BooleanField(default=False)
    invited_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    
    ....
    
    @staticmethod
    def create(user, source, first_name=None, last_name='', phone=None, email=None):
    
    ....
    
    @staticmethod
    def state_transition(invitor, invitee):
    
    ....
    
    @staticmethod
    def get_contacts(user, state=None, offset=None):
    
    ....
    
    @staticmethod
    def invite_contacts(user, invite_all=False, deselectd_ids=[], selected_ids=[]):
    
    ....
```

##### 3. Creating a Celery Task

> Code snippet from contacts/tasks.py
```
def import_contacts_from_phone(user_id, contacts=[]):
    user = User.objects.get(id=user_id)
    record = models.UserContactsImport.objects.get_or_create(user=user)[0]
    record.phone_import_recorded = False
    record.save()

    for contact in contacts:
        print(contact)
        try:
            models.UserContact.create(user=user, source='PHONE', first_name=contact['name'], phone=contact['phone'])
        except Exception as e:
            print(e)

    record.phone_import_recorded = True
    record.save()
    firebase.contacts_upload_trigger(to_user=user)
    return True
```
##### 4. Writing APIs and defining end points

> Code snippet from contacts/api_urls.py
```
urlpatterns = [
    url(r'^import/$', rest_views.import_contacts),
    url(r'^phone-import-recorded/$', rest_views.check_phone_import_recorded),
]
```

##### 5. Preparing for server

> Code snippet from Procfile
```
web: gunicorn commune.wsgi --log-file -
worker: celery worker --app=app.celery.app
```
Here 2nd line 3rd **app** is the actual name of your Django app. In our case its call **app** :)

## JWT AUTH
JWT stand for JSON Web Token and it is an authentication strategy used by client/server applications where the client is a Web application using JavaScript or mobile platforms like Android or iOS.

In this app we are going to explore the specifics of JWT authentication and how we have integrated the same withing Django to use either of Phone, Email, Google or Facebook auth.

A JWT Token looks something like this xxxxx.yyyyy.zzzzz, those are three distinctive parts that compose a JWT:
```
header.payload.signature
```

#### Libraries Used:
1. djangorestframework==3.9.4
2. djangorestframework-jwt==1.11.0
3. PyJWT==1.7.1

#### Development:
##### 1. Installing Libraries
We will first start with first installing with proper jwt libraries for django and including them in app/settings.py as shown here

> Code snippet from settings.py
```
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication'
        ...
        ...
    ],
}
```

```
JWT_AUTH = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_LEEWAY': 300,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=300),
    'JWT_AUDIENCE': None,
    'JWT_ISSUER': None,
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=300),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',
}
```
##### 2. Writing JWT Utils
There are set of functions in authe/jwt_utils.py file that are relevant here. We in this document we will restrict to explaing the purpose of class JWTAuthentication.

> Code snippet from authe/jwt_utils.py
```
class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            JWToken = request.META.get('HTTP_AUTHORIZATION')[5:].split('>')[0]
        except Exception:
            JWToken = None
        # If no token return None - no user was authenticated with the JWT
        if not JWToken:
            return None
        try:
            user = get_user_from_token(JWToken)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User Blocked')
        return user, None

    def enforce_csrf(self, request):
        return
```

##### 3. Writing APIs and defining endpoints

> Code snippet from authe/api_urls.py
```
urlpatterns = [
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
    url(r'^phone-auth/', rest_views.PhoneAuth.as_view()),
    url(r'^password-set/', rest_views.set_password),
    url(r'^password-reset/', rest_views.reset_password)
]
```

##### 4. Handling token on client side

So basically your response body looks something like this. After that you are going to store the access token on the client side, usually in the localStorage.
```
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQ1MjI0MjU5LCJqdGkiOiIyYmQ1NjI3MmIzYjI0YjNmOGI1MjJlNThjMzdjMTdlMSIsInVzZXJfaWQiOjF9.D92tTuVi_YcNkJtiLGHtcn6tBcxLCBxz9FKD3qzhUg8",
    "user_id": "XXXX",
    "username": "NAMEXXXXX"
}

```

In order to access the protected views on the backend (i.e., the API endpoints that require authentication), you should include the access token in the header of all requests, like this:
```
http://127.0.0.1:8000/hello/ "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTQ1MjI0MjAwLCJqdGkiOiJlMGQxZDY2MjE5ODc0ZTY3OWY0NjM0ZWU2NTQ2YTIwMCIsInVzZXJfaWQiOjF9.9eHat3CvRQYnb5EdcgYFzUyMobXzxlAVh_IAgqyvzCE"
```
