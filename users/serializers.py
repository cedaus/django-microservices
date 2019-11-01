from rest_framework import serializers
from django.contrib.auth.models import User


class UserMiniSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    heading = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.userprofile.get_name()

    def get_heading(self, obj):
        return obj.userprofile.get_heading()

    def get_profile_image(self, obj):
        return obj.userprofile.get_profile_image()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'name', 'heading',
                  'profile_image']
