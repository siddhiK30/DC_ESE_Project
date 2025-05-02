# from rest_framework import serializers
# from django.contrib.auth.models import User
# from .models import GuestbookEntry

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email']

# class GuestbookEntrySerializer(serializers.ModelSerializer):
#     sender = UserSerializer(read_only=True)
#     recipients = UserSerializer(many=True, read_only=True)

#     class Meta:
#         model = GuestbookEntry
#         fields = '__all__'

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import GuestbookEntry

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class GuestbookEntrySerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipients = UserSerializer(many=True, read_only=True)
    synchronized_timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    sender_local_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    
    class Meta:
        model = GuestbookEntry
        fields = [
            'id', 
            'sender', 
            'recipients', 
            'content', 
            'created_at', 
            'synchronized_timestamp',
            'sender_local_time'
        ]