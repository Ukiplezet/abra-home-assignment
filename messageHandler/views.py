
from user.models import UserManager, UserMessages
from .models import Message
from django.utils.translation import gettext as _
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from . import utils
from .serializers import (
    MessageSerializer,
)

from rest_framework.parsers import JSONParser


@ csrf_exempt
def get_all_messages(request, pk=None):
    """Retrieve messages for authenticated user."""
    received_token = utils.confirm_token_exists_in_request(request)
    validated_user_token = utils.validate_user_credentials(received_token, pk)

    if validated_user_token:
        messages = utils.get_all_user_messages_from_db(pk)
        serializer = MessageSerializer(
            messages, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=200)


@ csrf_exempt
def get_all_unread_messages(request, pk=None):
    """Retrieve unread messages for authenticated user."""

    received_token = utils.confirm_token_exists_in_request(request)
    validated_user_token = utils.validate_user_credentials(received_token, pk)

    if validated_user_token:
        unread_messages_list = utils.get_users_unread_messages(pk)
        serializer = MessageSerializer(
            unread_messages_list, many=True, context={'request': request})
        return JsonResponse(serializer.data, safe=False, status=200)


@ csrf_exempt
def read_a_message(request, pk=None):
    """"Read receiver's oldest unread message and change is_read to true."""

    received_token = utils.confirm_token_exists_in_request(request)
    validated_user_token = utils.validate_user_credentials(received_token, pk)

    if validated_user_token:
        messages = utils.get_users_unread_messages(pk)

        if messages:
            message = messages[0]
            message.is_read = True
            message.save()
            serializer = MessageSerializer(
                messages, many=True, context={'request': request})

            return JsonResponse(serializer.data[0], safe=False, status=201)
        return JsonResponse('User doesn`t have any messages', safe=False, status=400)


@ csrf_exempt
def delete_a_message(request, pk=None):
    """delete user's oldest message from DB."""
    received_token = utils.confirm_token_exists_in_request(request)
    validated_user_token = utils.validate_user_credentials(received_token, pk)

    if validated_user_token:
        messages = utils.get_first_message_between_users(pk)

        if messages:
            messages[0].delete()
            return JsonResponse('Message earased successfully', safe=False, status=200)
        return JsonResponse('User doesn`t have any messages', safe=False, status=400)


@ csrf_exempt
def write_a_message(request, pk=None):
    """Write a new message."""
    received_token = utils.confirm_token_exists_in_request(request)
    validated_user_token = utils.validate_user_credentials(received_token, pk)
    if validated_user_token:
        data = JSONParser().parse(request)
        is_user_name_validated = utils.validate_sender_name_in_request(
            data, pk)
        if is_user_name_validated:
            serializer = MessageSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                utils.set_last_message_id_between_users(serializer)
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
