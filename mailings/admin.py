
from django.contrib import admin

from .models import Mailing, Client, Message, MailingAttempt


class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'status', 'subject')
    list_filter = ('status', 'start_time')
    search_fields = ('subject', 'text')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone', 'tag')
    list_filter = ('tag',)
    search_fields = ('email', 'phone')

    admin.site.register(Mailing, MailingAdmin)
    admin.site.register(Client,)
    admin.site.register(Message)
    admin.site.register(MailingAttempt)