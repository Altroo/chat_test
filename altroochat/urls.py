#! -*- coding: utf-8 -*-

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from altroochat.api import MessageModelViewSet, ChatUserModelViewSet


router = DefaultRouter()
router.register(r'message', MessageModelViewSet, basename='message-api')
router.register(r'user', ChatUserModelViewSet, basename='chat-user-api')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
