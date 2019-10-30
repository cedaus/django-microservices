# django-microservices
This project is not an Introduction to Django. To get the most out of it, you should be familiar with Django.
This project comprises of following microservices/micro-features built on top of Django Framework

1. Real Time Chat
2. Celery and Redis based contacts upload
3. JWT Authentication with Phone, Email, Google, Facebook
4. Notification feed
5. Elastic Search based text and tag search engine

## REALT TIME CHAT
In this part I will talk about developing a real time chat. You can check the chat working in this video.
#### Features of Chat App:
* Chat is based on channel which comprise of two participants
* Participants can send each other messages in text, file and image formats
* Participants can take actions like delete and forward a message

#### Libraries Used:
* Firebase
* AWS S3

##### Defining a django models
Each message object has an associated Foreignkey to Chat & User username, timestamp, and the actual message text.
```
class Message(models.Model):
    class Meta:
        get_latest_by = "message_number"
        verbose_name = "Message"

    created = models.DateTimeField(auto_now_add=True, editable=False)
    from_user = models.ForeignKey(User, related_name='from_user', null=False, blank=False)
    type = models.CharField(choices=constants.chat_type_states_choices,max_length=30,default=constants.chat_type_states['TEXT'])
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
##### Writing REST APIs
