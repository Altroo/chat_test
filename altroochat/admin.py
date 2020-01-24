from django.contrib.admin import ModelAdmin, site
from altroochat.models import MessageModel, Status


class MessageModelAdmin(ModelAdmin):
    readonly_fields = ('created',)
    search_fields = ('id', 'body', 'user__username', 'recipient__username')
    list_display = ('id', 'user', 'viewed', 'recipient', 'created', 'updated', 'characters')
    list_display_links = ('id',)
    list_filter = ('user', 'recipient')
    date_hierarchy = 'created'


site.register(MessageModel, MessageModelAdmin)
site.register(Status)
