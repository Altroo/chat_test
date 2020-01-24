#! -*- coding: utf-8 -*-

from altroochat import consumers
from django.conf.urls import re_path

websocket_urlpatterns = [
    re_path(r'^altroochatws$', consumers.AltrooChatConsumer),
]
