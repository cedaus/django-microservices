from django.conf.urls import url
from . import rest_views


urlpatterns = [
    url(r'^list/$', rest_views.get_chat_list),
    url(r'^create/(?P<member_id>[-\w\d]+)/$', rest_views.create_chat),
    url(r'^(?P<chat_id>[-\w\d]+)/$', rest_views.get_chat),
    url(r'^message/add/(?P<chat_id>[-\w\d]+)/', rest_views.add_message),
    url(r'^message/new/(?P<chat_id>[-\w\d]+)/', rest_views.get_new_message),
    url(r'message/old/(?P<chat_id>[-\w\d]+)/$', rest_views.get_old_message)
]