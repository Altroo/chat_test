#! -*-coding: utf-8-*-

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from altroochat.models import MessageModel, Status
from channels.db import database_sync_to_async
from django.contrib.auth.models import User


class AltrooChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer used to Altoo chat functionality
    this consumer provide the websocket for
    unentrupted communication.
    """
    async def connect(self):
        user = self.scope["user"]
        self.group_name = "%s" % (user.id)
        print("group name is %s and channel_name is %s" % (self.group_name, self.channel_name))
        
        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.create_or_update_status(user.id, online=True)


    async def disconnect(self, close_code):
        """
        Method called every time a connection to websocket
        Is closed by the user or user is disconnected.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        await self.create_or_update_status(self.group_name,
                                           online=False)

    async def receive(self, text_data=None, bytes_data = None):
        """
        Method used to receive the message through
        websocket interface
        """
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'recieve_group_message',
                'message': message
            }
        )

    async def recieve_group_message(self, event):
        """
        Method used to broadcast the message the the group
        """
        message = event['message']
        await self.send(
            text_data=json.dumps({
                'message': message
            }))


    @database_sync_to_async
    def create_or_update_status(self, user_id, online):
        """
        We update the status model for this user or create
        status models instance for the user, every time he is
        connected or disconnected with the websocket.
        """
        try:
            status = Status.objects.get(user__id=user_id)
            if status.online is online:
                pass
            else:
                status.online = online
                status.save()
        except Status.DoesNotExist:
            Status.objects.create(user=User.objects.get(id=user_id),
                            online=online)

