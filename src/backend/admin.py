from django.contrib import admin

# Register your models here.
from backend.models import TGUser, Message, Event, Invite, Prizes


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
        'win_random_prize',
        'last_checked_email',
    ]

    list_filter = [
        'is_admin',
        'is_authorized',
        'is_notified',
        'win_random_prize'
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

@admin.register(Prizes)
class PrizesAdmin(admin.ModelAdmin):
    list_display = ['merch_size', 'quantity']
    search_fields = ['merch_size']
