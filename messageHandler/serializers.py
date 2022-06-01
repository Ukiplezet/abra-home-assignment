from rest_framework import serializers
from .models import Message
from user.models import User


#
# Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    """For Serializing Message"""
    sender = serializers.SlugRelatedField(
        many=False, slug_field='name', queryset=User.objects.all())
    receiver = serializers.SlugRelatedField(
        many=False, slug_field='name', queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'subject',
                  'message', 'timestamp', 'is_read']
