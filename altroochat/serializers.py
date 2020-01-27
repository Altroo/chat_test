# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from altroochat.models import MessageModel, Status
from rest_framework.serializers import (ModelSerializer,
                                        CharField, SerializerMethodField,
                                        CreateOnlyDefault,  CurrentUserDefault)
from rest_framework.authtoken.models import Token


class AltrooChatLoginSerializer(ModelSerializer):
    token = SerializerMethodField()

    def get_token(self, instance):
        try:
            return instance.auth_token.key
        except Token.DoesNotExist:
            token = Token.objects.create(user=instance)
            return token.key
            

    class Meta:
        model = User
        exclude = ('password', )


class MessageModelSerializer(ModelSerializer):
    initiator = SerializerMethodField()

    def get_initiator(self, instance):
        return instance.user.username

    class Meta:
        model = MessageModel
        fields = ('id', 'user', 'initiator',
                  'recipient', 'created', 'updated',
                  'body', 'viewed', 'viewed_timestamp', "attachment")
        extra_kwargs = {
        'user': {
            'default': CreateOnlyDefault(
                CurrentUserDefault()
            ),
        }
    }


class ChatUserModelSerializer(ModelSerializer):
    has_conversation = SerializerMethodField()
    online = SerializerMethodField()

    def get_has_conversation(self, instance):
        user = self.context.get('request').user
        return MessageModel.objects.filter(user=user, recipient=instance).exists()

    def get_online(self, instance):
        try:
            if(instance.status):
                return instance.status.online
            else:
                return False
        except Status.DoesNotExist:
            return False

    class Meta:
        model = User
        fields = ('id', 'username', 'has_conversation', 'online')
