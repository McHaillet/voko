from django.contrib import admin
from log.models import EventLog


class EventLogAdmin(admin.ModelAdmin):
    list_display = ["created", "event", "operator", "user"]
    ordering = ("-id", )

admin.site.register(EventLog, EventLogAdmin)