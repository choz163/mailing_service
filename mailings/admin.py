from django.contrib import admin

from .models import Mailing, Client, Message, MailingAttempt


class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "start_at", "status")
    list_filter = ("status", "start_at")
    search_fields = ("end_at", "message")


class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone", "full_name")
    list_filter = ("full_name",)
    search_fields = ("email", "phone")

    admin.site.register(Mailing, MailingAdmin)
    admin.site.register(
        Client,
    )
    admin.site.register(Message)
    admin.site.register(MailingAttempt)
