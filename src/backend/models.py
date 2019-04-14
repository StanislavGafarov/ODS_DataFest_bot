import datetime

from django.db import models


# Create your models here.


def make_str(*fields):
    def dec(cls):
        def __str__(self):
            return ' '.join(str(getattr(self, f)) for f in fields)

        setattr(cls, '__str__', __str__)
        return cls

    return dec


@make_str('name', 'last_name', 'username')
class TGUser(models.Model):
    tg_id = models.IntegerField(unique=True)
    name = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    username = models.TextField(blank=True)

    is_admin = models.BooleanField(default=False)
    is_authorized = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)
    has_news_subscription = models.BooleanField(default=False)
    invite = models.OneToOneField('Invite', on_delete=models.SET_NULL, null=True, default=None, related_name='email')

    #RANDOM BEER INFO
    in_random_beer = models.BooleanField(default=False)

    last_checked_email = models.TextField(null=True, default=None)
    state = models.IntegerField(null=True, default=None)

    #Random prize
    in_random_prize = models.BooleanField(default=False)
    merch_size = models.TextField(null=True, default=None)
    win_random_prize = models.BooleanField(default=False)


@make_str('user', 'text')
class Message(models.Model):
    user = models.ForeignKey(TGUser, on_delete=models.CASCADE, related_name='messages')
    tg_id = models.IntegerField()
    text = models.TextField()
    date = models.DateTimeField()

    class Meta:
        unique_together = (('user', 'tg_id'),)

    @staticmethod
    def from_update(api: 'TelegramBotApi', update) -> 'Message':
        user = api.get_user(update.message.chat_id)
        tg_id = update.message.message_id
        date: datetime.datetime = update.message.date
        date = date.replace(tzinfo=datetime.timezone.utc)
        return Message(user=user, tg_id=tg_id, text=update.message.text, date=date).save()


@make_str('email')
class Invite(models.Model):
    email = models.TextField(unique=True)
    code = models.IntegerField(unique=True, default=False)
    name = models.TextField(default=False)
    surname = models.TextField(default=False)


@make_str('news')
class News(models.Model):
    news = models.TextField(default=False)


SIZES = [(i,i) for i in ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']]


@make_str('merch_size')
class Prizes(models.Model):
    merch_size = models.TextField(choices=SIZES)
    quantity = models.IntegerField(default=0)


EVENT_TYPES = {
    'talk': 'доклад',
    'section': 'секция',
    'workshop': 'воркшоп'
}

df_day = datetime.datetime(2019, 5, 10, 12)


@make_str('event_type', 'title')
class Event(models.Model):
    event_type = models.TextField(choices=EVENT_TYPES.items())
    title = models.TextField()
    speaker = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    location = models.TextField(blank=True)
    section = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    start = models.DateTimeField(default=df_day)
    end = models.DateTimeField(null=True, default=None, blank=True)


from backend.tgbot.base import TelegramBotApi
