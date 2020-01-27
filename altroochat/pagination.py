# -*- coding: utf-8 -*-

from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """
    page_size = settings.MESSAGES_TO_LOAD
