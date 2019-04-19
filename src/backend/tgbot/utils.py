import logging
import os
from functools import wraps
import requests

from bot import settings

from backend.models import Message
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
            user.save()
            return new_state
        return get_user

    @classmethod
    def with_random_beer_user(cls, f):
        @wraps(f)
        def get_random_beer_user(cls, api: TelegramBotApi, update, user):
            random_beer_user = api.get_random_beer_user(user)
            return f(cls, api, random_beer_user, user, update)
        return get_random_beer_user

    def composed(*decs):
        def deco(f):
            for dec in reversed(decs):
                f = dec(f)
            return f
        return deco