import datetime
import json

from django.db import models
from telegram import Location

from backend.tgbot.texts import TEXT_NEWS_FAIL_LOAD

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
    invite = models.OneToOneField('Invite', on_delete=models.SET_NULL, null=True, default=None, related_name='tguser')

    is_banned = models.BooleanField(default=False)

    #RANDOM BEER INFO
    in_random_beer = models.BooleanField(default=False)

    last_checked_email = models.TextField(null=True, default=None)
    state = models.IntegerField(null=True, default=None)

    #Random prize
    in_random_prize = models.BooleanField(default=False)
    merch_size = models.TextField(null=True, default=None)
    win_random_prize = models.BooleanField(default=False)

    # Nvidia jetsone
    in_nvidia_jetsone = models.BooleanField(default=False)

    # On Major
    on_major = models.BooleanField(default=False)


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
        text = update.message.text
        text = text if text else 'not-text'
        return Message(user=user, tg_id=tg_id, text=text, date=date).save()


@make_str('email')
class Invite(models.Model):
    email = models.TextField(unique=True)
    code = models.IntegerField(unique=True, default=False)
    name = models.TextField(default=False)
    surname = models.TextField(default=False)


# TODO: Переписать красиво
class NewsGroup:
    __groups = ['NONE', 'NEWS_SUBSCRIPTION', 'ADMINS', 'WINNERS', 'ALL']

    @staticmethod
    def no_group():
        return NewsGroup.__groups[0]

    @staticmethod
    def news_subscription():
        return NewsGroup.__groups[1]

    @staticmethod
    def admins():
        return NewsGroup.__groups[2]

    @staticmethod
    def winners():
        return NewsGroup.__groups[3]

    @staticmethod
    def all_users():
        return NewsGroup.__groups[4]

    @staticmethod
    def choices():
        return [(i, i) for i in NewsGroup.__groups]


# TODO: Переписать красиво
class NewsType:
    __types = ['TEXT', 'IMAGE', 'STICKER', 'LOCATION']

    @staticmethod
    def text():
        return NewsType.__types[0]

    @staticmethod
    def image():
        return NewsType.__types[1]

    @staticmethod
    def sticker():
        return NewsType.__types[2]

    @staticmethod
    def location():
        return NewsType.__types[3]

    @staticmethod
    def choices():
        return [(i, i) for i in NewsType.__types]


@make_str('news')
class News(models.Model):
    # news creator
    reporter_user_id = models.IntegerField()
    # news target group
    target_group = models.TextField(choices=NewsGroup.choices(), default=NewsGroup.no_group())
    # message type [text|image|location|sticker]
    news_type = models.TextField(choices=NewsType.choices(), default=NewsType.text())
    # text value
    news = models.TextField(default='', blank=True)

    __get_users_map = {NewsGroup.no_group(): lambda: TGUser.objects.none(),
                       NewsGroup.news_subscription(): lambda: TGUser.objects.filter(has_news_subscription=True),
                       NewsGroup.admins(): lambda: TGUser.objects.filter(is_admin=True),
                       NewsGroup.winners(): lambda: TGUser.objects.none(),
                       NewsGroup.all_users(): lambda: TGUser.objects.all()}

    def get_sender(self):
        def send_text(api, user, reply_markup=None):
            api.bot.send_message(user, self.news, reply_markup=reply_markup)

        def send_sticker(api, user, reply_markup=None):
            api.bot.send_sticker(user, self.news, reply_markup=reply_markup)

        def send_location(api, user, reply_markup=None):
            def get_location():
                json_acceptable_string = self.news.replace("'", "\"")
                try:
                    data = json.loads(json_acceptable_string)
                    return data['longitude'], data['latitude']
                except:
                    return None, None
            longitude, latitude = get_location()
            if longitude:
                api.bot.send_location(user, longitude=longitude, latitude=latitude, reply_markup=reply_markup)
            else:
                api.bot.send_message(user, TEXT_NEWS_FAIL_LOAD, reply_markup=reply_markup)

        def send_image(api, user, reply_markup=None):
            def get_image():
                json_acceptable_string = self.news.replace('None', "'None'").replace("'", "\"")
                try:
                    data = json.loads(json_acceptable_string)
                    return data['image'], data['caption']
                except:
                    return None, None
            photo, caption = get_image()
            if photo:
                api.bot.send_photo(user, photo, caption, reply_markup=reply_markup)
            else:
                api.bot.send_message(user, TEXT_NEWS_FAIL_LOAD, reply_markup=reply_markup)

        __get_sender_map = {NewsType.text(): send_text,
                            NewsType.sticker(): send_sticker,
                            NewsType.location(): send_location,
                            NewsType.image(): send_image
                            }
        return __get_sender_map[str(self.news_type)]

    def get_users(self):
        try:
            return News.__get_users_map[str(self.target_group)]()
        except ValueError:
            pass
        return TGUser.objects.none()


SIZES = [(i, i) for i in ['XS', 'S', 'M', 'L', 'XL', 'XXL']]


@make_str('merch_size')
class Prizes(models.Model):
    merch_size = models.TextField(choices=SIZES)
    quantity = models.IntegerField(default=0)

@make_str('tg_user_id')
class RandomBeerUser(models.Model):
    tg_user_id = models.IntegerField(unique=True)
    tg_nickname = models.TextField(null=True, default=None)
    ods_nickname = models.TextField(null=True, default=None)
    social_network_link = models.TextField(null=True, default=None)
    random_beer_try = models.IntegerField(default=0)
    prev_pair = models.IntegerField(null=True, default=None)
    accept_rules = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    email = models.TextField(null=True, default=None)




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
