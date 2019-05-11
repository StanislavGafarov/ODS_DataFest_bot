from django.contrib import admin

# Register your models here.
from backend.models import TGUser, Message, Event, Invite, Prizes, RandomBeerUser, News


@admin.register(TGUser)
class TGUserAdmin(admin.ModelAdmin):
    list_display = [
        'tg_id',
        'name',
        'username',
        'last_checked_email',

        'is_admin',
        'is_authorized',
        'is_notified',
        'has_news_subscription',
        'win_random_prize',
        'on_major'
    ]

    list_filter = [
        'is_admin',
        'is_authorized',
        'is_notified',
        'win_random_prize',
        'on_major'
    ]

    search_fields = ['name', 'last_name', 'username', 'last_checked_email', 'on_major', 'win_random_prize']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'date']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['reporter_user_id', 'target_group', 'news_type', 'news']
    list_filter = ['reporter_user_id', 'target_group']


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['code', 'email', 'name', 'surname']
    search_fields = ['code', 'email', 'name', 'surname']

@admin.register(Prizes)
class PrizesAdmin(admin.ModelAdmin):
    list_display = ['merch_size', 'quantity']
    search_fields = ['merch_size']

@admin.register(RandomBeerUser)
class RandomBeerUserAdmin(admin.ModelAdmin):
    list_display = ['tg_user_id', 'email', 'tg_nickname', 'ods_nickname', 'social_network_link', 'random_beer_try', 'prev_pair',
                    'accept_rules', 'is_busy']
    search_fields = ['accept_rules', 'is_busy', 'email']

    actions = ['zero_beer']

    def zero_beer(self, request, queryset):
        queryset.update(random_beer_try=0, is_busy=False)
    zero_beer.short_description = "Zero random beer meeting count"