from django.contrib import admin

from .models import SentMail

@admin.register(SentMail)
class SentMailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email_address', 'user', 'timestamp')
