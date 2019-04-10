from django.contrib import admin

# Register your models here.
from backend.models import TGUser, Message, Event, Invite


@admin.register(TGUser)
class TGUserAdmin(admin.ModelAdmin):
    list_display = [
        'tg_id',
        'name',
        'last_name',
        'username',

        'is_admin',
        'is_authorized',
        'is_notified',
        'has_news_subscription',
        'last_checked_email',
    ]

    list_filter = [
        'is_admin',
        'is_authorized',
        'is_notified'
    ]

    search_fields = ['name', 'last_name', 'username', 'last_checked_email']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'date']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'surname']
    search_fields = ['email', 'name', 'surname']
