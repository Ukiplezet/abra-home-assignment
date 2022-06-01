from django.db.models import Q
from django.http.response import JsonResponse

from urllib.error import HTTPError

from rest_framework.authtoken.models import Token
from rest_framework import (
    status,
    serializers,
)
from rest_framework.exceptions import (
    NotAuthenticated,
    AuthenticationFailed,

)

from user.serializers import UserMessageSerializer
from user.models import User, UserMessages
from .models import Message


def get_user_name_by_name_from_db(name=None):
    user = User.objects.get(
        name=name
    )
    return user


def get_user_name_by_id_from_db(pk=None):
    user = User.objects.get(
        id=pk
    )
    return user


def get_user_token_from_db(user=None):
    auth_user = Token.objects.get(
        user=user
    )
    return auth_user


def get_token_by_user_id_from_db(pk=None):
    user = get_user_name_by_id_from_db(pk)
    return get_user_token_from_db(user)


def validate_user_credentials(received_token=None, pk=None):
    """Comparing received token with the token stored in DB."""
    auth_token = Token.objects.get(
        key=received_token,
    )
    expected_user_token = get_token_by_user_id_from_db(pk)

    if auth_token != expected_user_token:
        raise AuthenticationFailed()
    return expected_user_token


def confirm_token_exists_in_request(request):
    """Checking that request came with a token."""
    received_token = request.META.get('HTTP_AUTHORIZATION')

    if not received_token:
        raise NotAuthenticated()
    received_token = received_token.split(' ')[1]
    return received_token


def validate_sender_name_in_request(data=None, pk=None):
    """Comparing sender name with user's name in DB."""
    request_user_name = data['sender']
    user_by_name = get_user_name_by_name_from_db(request_user_name)
    user_by_id = get_user_name_by_id_from_db(pk)

    if user_by_name != user_by_id:
        msg = _('User does not match data provided in the request.')
        raise serializers.ValidationError(
            msg, code=status.HTTP_400_BAD_REQUEST)
    else:
        return True


def get_list_of_messages_ids_by_user(pk=None):
    all_messages_ids = UserMessages.objects.filter(
        user_id=pk).values_list('message_id', flat=True)
    return all_messages_ids


def get_users_unread_messages(pk=None):
    all_messages_ids = get_list_of_messages_ids_by_user(pk)
    all_messages_ids = list(all_messages_ids)
    messages = Message.objects.filter(
        Q(id__in=all_messages_ids) &
        Q(is_read=False)
    )
    return messages


def get_all_user_messages_from_db(pk=None):
    all_messages_ids = get_list_of_messages_ids_by_user(pk)
    all_messages_ids = list(all_messages_ids)
    messages = Message.objects.filter(
        Q(id__in=all_messages_ids)
    )
    return messages


def get_user_id_by_name(name=None):
    user_id = User.objects.filter(
        name=name
    ).values_list('id', flat=True)
    return user_id[0]


def set_last_message_id_between_users(serializer):
    """Retrieve sender and receiver id by name from message and save with message id to DB."""
    sender_id = get_user_id_by_name(serializer.data['sender'])
    receiver_id = get_user_id_by_name(serializer.data['receiver'])

    set_last_message_between_users_to_db(serializer, sender_id)
    set_last_message_between_users_to_db(serializer, receiver_id)
    return


def set_last_message_between_users_to_db(serializer, user_id):
    saved_message_user_reference = {}
    saved_message_user_reference['user_id'] = user_id
    saved_message_user_reference['message_id'] = serializer.data['id']
    sender_message = UserMessageSerializer(
        data=saved_message_user_reference)
    if sender_message.is_valid():
        sender_message.save()
        return JsonResponse(sender_message.data, status=201)
    return HTTPError


def get_first_message_between_users(pk=None):
    last_message = UserMessages.objects.filter(
        user_id=pk)
    return last_message


def delete_message_from_database(message_id):

    message_sender_id = Message.objects.filter(
        id=message_id
    ).values_list('sender_id', flat=True)[0]
    message_receiver_id = Message.objects.filter(
        id=message_id
    ).values_list('receiver_id', flat=True)[0]
    message_to_delete = UserMessages.objects.filter(
        (Q(user_id=message_receiver_id) | Q(user_id=message_sender_id)) &
        Q(message_id=message_id)
    ).values()

    if message_to_delete:
        if len(message_to_delete) == 1:
            message_to_delete = Message.objects.filter(
                id=message_id
            ).delete()
        return message_id
    return
