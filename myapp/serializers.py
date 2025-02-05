from rest_framework import serializers
from django.contrib.auth.models import User
from .models import GuestbookEntry

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class GuestbookEntrySerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipients = UserSerializer(many=True, read_only=True)

    class Meta:
        model = GuestbookEntry
        fields = '__all__'
