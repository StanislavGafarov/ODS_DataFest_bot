import logging
import os
from functools import wraps

import requests

from bot import settings

from backend.models import Message, RandomBeerUser, News, TGUser
from backend.tgbot.base import TelegramBotApi


def get_public_host():
    r = requests.get('http://whatismyip.akamai.com/')
    if r.status_code != 200:
        r.raise_for_status()
    return r.text


def check_certs():
    if settings.TG_WEBHOOK:
        if not os.path.isfile(settings.TG_WEBHOOK_CERT_KEY) or not os.path.isfile(settings.TG_WEBHOOK_CERT_PEM):
            raise Exception('Missing certificates for bot at \n{}\n{}'.format(settings.TG_WEBHOOK_CERT_KEY,
                                                                              settings.TG_WEBHOOK_CERT_PEM))

        from OpenSSL import crypto

        with open(settings.TG_WEBHOOK_CERT_PEM, 'rb') as c:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, c.read())
            subject = cert.get_subject()
            issued_to = subject.CN  # the Common Name field
            if issued_to != get_public_host():
                raise Exception(
                    'Not valid certificates: issued to "{}", but host ip is "{}"'.format(issued_to, settings.HOST_IP))

# root_logger = logging.getLogger('root').setLevel(logging.ERROR)
# updater_logger = logging.getLogger('telegram.ext.updater').setLevel(logging.ERROR)
# urllib3_logger = logging.getLogger('telegram.vendor.ptb_urllib3.urllib3.connectionpool').setLevel(logging.ERROR)
logger = logging.getLogger('bot')


class Decorators(object):
    @classmethod
    def save_msg(cls, f):
        @wraps(f)
        def save(cls, api: TelegramBotApi, update):
            Message.from_update(api, update)
            return f(cls, api, update)

        return save

    @classmethod
    def with_user(cls, f):
        @wraps(f)
        def get_user(cls, api: TelegramBotApi, update):
            user = api.get_user(update.message.chat_id)
            new_state = f(cls, api, user, update)
            user.state = new_state
            # с юзером могли произойти изменения по время выполнения f
            # так что лучше ограничиться обновлением только одного поля
            user.save(update_fields=['state'])
            return new_state
        return get_user

    @classmethod
    def with_random_beer_user(cls, f):
        @wraps(f)
        def get_random_beer_user(cls, api: TelegramBotApi, user, update):
            random_beer_user = RandomBeerUser.objects.filter(tg_user_id=user.tg_id).first()
            if random_beer_user is None:
                logger.info('User {} not in random beer users, creating new one'.format(user))
                random_beer_user = RandomBeerUser(tg_user_id=user.tg_id)
                random_beer_user.email = user.last_checked_email
                random_beer_user.save()
            return f(cls, api, user, update, random_beer_user)
        return get_random_beer_user

    @classmethod
    def with_news(cls, f):
        @wraps(f)
        def get_news(cls, api: TelegramBotApi, user, update):
            news = News.objects.filter(reporter_user_id=user.tg_id, news='').order_by('-id').first()
            if not news:
                news = News(reporter_user_id=user.tg_id)
                news.save()
            return f(cls, api, user, update, news)
        return get_news

    def composed(*decs):
        def deco(f):
            for dec in reversed(decs):
                f = dec(f)
            return f
        return deco
