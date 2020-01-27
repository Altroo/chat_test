# -*- coding: utf-8 -*-

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny
from django.conf import settings
from altroochat.serializers import (MessageModelSerializer,
                                    ChatUserModelSerializer,
                                    AltrooChatLoginSerializer)
from altroochat.models import MessageModel
from altroochat.pagination import MessagePagination


class MessageLoginModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AltrooChatLoginSerializer
    allowed_methods = ('OPTION', 'HEAD', 'POST', 'GET')
    permission_classes = [AllowAny, ]

    def list(self, request, *args, **kwargs):
        """
        when ever someone call this endpoint with get request
        he/she will only be provided with his details.
        """
        if self.request.user.is_authenticated:
            return  Response(self.get_serializer(request.user).data, status=status.HTTP_200_OK)
        else:
            return Response({"Error": "User is not authenticated to use this endpoint"},
                            status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """
        Method used to verify the user data provided in
        the API call and return user token based upon the
        authentication process
        """
        password = request.POST.get('password', None)
        username = request.POST.get('username', None)
        if password is not None and username is not None:
            user = authenticate(username=username, password=password)
            if user is not None:
                return Response(self.get_serializer(user).data,
                                status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'Error': "Either Username or Password is wrong"},
                                status=status.HTTP_401_UNAUTHORIZED)


    def retrieve(self, request, pk, *args, **kwargs):
        """
        User is only allowed to retrieve his information
        and when ever he/she will be try to get the user
        information of the other users. we will return HTTP
        BAD REQUEST in return
        """
        if request.user.is_authenticated and request.user.id == int(pk):
            return super(MessageLoginModelViewSet, self).retrieve(request, pk, *args, **kwargs)
        else:
            return Response({"Error": "Users are only allowed to get data of their account, And only when they are logged in"},
                            status=status.HTTP_400_BAD_REQUEST)


class MessageModelViewSet(ModelViewSet):
    serializer_class = MessageModelSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS', 'POST' 'PATCH')
    pagination_class = MessagePagination

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        target = self.request.query_params.get('target', None)
        if target is not None:
            if pk is not None:
                return MessageModel.objects.filter(
                    Q(recipient=self.request.user, user__id=target) |
                    Q(recipient__id=target, user=self.request.user)).filter(Q(recipient=self.request.user) |
                                                                            Q(user=self.request.user),
                                                                            Q(pk=pk))
            else:
                return MessageModel.objects.filter(
                    Q(recipient=self.request.user, user__id=target) |
                    Q(recipient__id=target, user=self.request.user))
        else:
            if pk is not None:
                return MessageModel.objects.filter(Q(recipient=self.request.user) |
                                                   Q(user=self.request.user)).filter(Q(recipient=self.request.user) |
                                                                                     Q(user=self.request.user),
                                                                                     Q(pk=pk))
            else:
                return MessageModel.objects.filter(Q(recipient=self.request.user) |
                                                   Q(user=self.request.user))



class ChatUserModelViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = ChatUserModelSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    pagination_class = None

    def list(self, request, *args, **kwargs):
        """
        Return all user data accept for the user
        who is making this request.
        """
        self.queryset = self.queryset.exclude(id=request.user.id)
        return super(ChatUserModelViewSet, self).list(request, *args, **kwargs)
