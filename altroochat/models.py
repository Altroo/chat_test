#! -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db.models import (Model, TextField, DateTimeField, ForeignKey,
                              CASCADE, BooleanField, OneToOneField, ImageField)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
import json


class MessageModel(Model):
    """
    This class represents a chat message.
    It has a owner (user), timestamp and
    the message body.
    """
    user = ForeignKey(User,
                      on_delete=CASCADE,
                      verbose_name='user',
                      related_name='sent_messages',
                      db_index=True)
    recipient = ForeignKey(User,
                           on_delete=CASCADE,
                           verbose_name='recipient',
                           related_name='recevied_messages',
                           db_index=True)
    created = DateTimeField('created',
                            auto_now_add=True,
                            editable=False,
                            db_index=True)
    updated = DateTimeField('updated', auto_now=True, editable=False)
    body = TextField('body', null=True, blank=True)
    attachment = ImageField(null=True, blank=True, upload_to="chat_attachment")
    viewed = BooleanField(default=False)
    viewed_timestamp = DateTimeField(null=True, blank=True)




    def __str__(self):
        return str(self.id)

    def clean(self):
        """
        we will overide the clean method of this
        model in order to provide the custom
        validation. here we will validate model
        to have atlest one of either attachment field
        or body field in the message otherwise message
        will not base saved in the database.
        """
        if((self.body is None or self.body == "") and (self.attachment is None or self.attachment == "")):
            raise ValidationError({"attachment": "Atleast attachment or body is required",
                                   "body": "Atleast attachment or body is required"})
        else:
            super(MessageModel, self).clean()

    def characters(self):
        """
        Instance Method to count body characters.
        :return: body's char number
        """
        return len(self.body)

    def notify_message_received(self):
        """
        Inform client there is a new message
        Using django channles websocket connection.
        """
        event = {
            'type': 'recieve_group_message',
            'message': {"type": "message",
                        "id": "%s" % (self.id),
                        "initiator": "%s" % (self.user.id),
                        "initiator_name": self.user.username
            }
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)("%s" % (self.recipient.id), event)

    def notify_viewed(self):
        """
        method used to notify the users of the message
        that the message has been viewed by the receipient
        """
        channel_layer = get_channel_layer()
        event = {
            "type": "recieve_group_message",
            "message": {
                "type": "seen",
                "id": "%s" % (self.id),
                "initiator": "%s" % (self.user.id),
                "initiator_name": self.user.username
            }
        }
        async_to_sync(channel_layer.group_send)("%s" % (self.user.id), event)
        async_to_sync(channel_layer.group_send)("%s" % (self.recipient.id), event)


    def save(self, *args, **kwargs):
        pk = self.id
        super(MessageModel, self).save(*args, **kwargs)
        if pk is None:
            self.notify_message_received()


    class Meta:
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ('-created',)



class Status(Model):
    """
    Model used to give online offline
    status on the go for the user.
    """
    
    user = OneToOneField(User,
                         on_delete=CASCADE,
                         verbose_name='user',
                         related_name="status")
    last_update = DateTimeField(auto_now=True, null=False, blank=False)
    online = BooleanField(default=False)


    def __str__(self):
        return "%s - %s" % (self.id, self.online)


    def notify_ws_client(self, instance=None):
        """
        Used to notify other users that this
        user is online now. we will pass instance to
        this method in case of the pre_save database
        trigger becuase data in the database is different
        then in the model instance.
        """
        channel_layer = get_channel_layer()
        for user_id in User.objects.filter(status__online=True).values_list('id', flat=True):
            if Status.objects.filter(user__id=user_id).exists() and Status.objects.get(user__id=user_id).online:
                event = {
                    'type': 'recieve_group_message',
                    'message': {
                        'type': 'status',
                        'user_id': self.id,
                        'online': self.online if instance is None else instance.online
                    }
                }
                async_to_sync(channel_layer.group_send)("%s" % (user_id), event)
        
                
            
    def save(self, *args, **kwargs):
        pk = self.id
        super(Status, self).save(*args, **kwargs)
        if pk is None:
            self.notify_ws_client(instance=None)

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"


@receiver(pre_save, sender=Status)
def call_ws_client(sender, instance, raw, using, update_fields, **kwargs):
    if instance.pk is not None:
        # if this is not the first time
        # when this instance is saved in the
        # DB we will check if the online flag is updated
        # if yes we will notify all other users connected
        # that user is online or offline.

        previous_status = Status.objects.get(id=instance.id)
        if previous_status.online is instance.online:
            pass
        else:
            instance.notify_ws_client(instance=instance)
    else:
        # notfication will be handle
        # in the save method of the model.
        pass


@receiver(pre_save, sender=MessageModel)
def notify_message(sender, instance, raw, using, update_fields, **kwargs):
    """
    DB Trigger to send the message to the user of the message model instance
    using Django channels Websocket that we your message has seen by the recipient.
    """
    if instance.pk is not None:
        # if this is not the first time
        # this instance is saved in the DB
        # we will check, if the viewed flag is updated?
        # if "YES". we will update all of the previous MessageModel isntace's
        # viewed flag to true and notify the user and recipient that message is
        # viewed, using channels. This block will only be used to provide seen status to user.

        old_instance = MessageModel.objects.get(id=instance.id)
        if old_instance.viewed is False and instance.viewed is True:
            instance.notify_viewed()
            old_unseen_messages = MessageModel.objects.filter(id__lt=instance.id,
                                                              viewed=False)
            for message in old_unseen_messages:
                message.notify_viewed()
            old_unseen_messages.update(viewed=True, viewed_timestamp=timezone.now())
        else:
            pass
    else:
        # notification will be handled
        # in the save method. and a new
        # message notification will we
        # sent to receipient
        pass
