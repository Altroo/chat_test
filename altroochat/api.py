from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication
from django.conf import settings
from altroochat.serializers import MessageModelSerializer, ChatUserModelSerializer
from altroochat.models import MessageModel


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme used by DRF. DRF's SessionAuthentication uses
    Django's session framework for authentication which requires CSRF to be
    checked. In this case we are going to disable CSRF tokens for the API.
    """

    def enforce_csrf(self, request):
        return


class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """
    page_size = settings.MESSAGES_TO_LOAD


class MessageModelViewSet(ModelViewSet):
    serializer_class = MessageModelSerializer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS', 'PATCH')
    authentication_classes = (CsrfExemptSessionAuthentication,)
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
