import logging
import os
from functools import wraps

import requests
from telegram.ext import RegexHandler

from backend.models import Message
from backend.tgbot.base import TelegramBotApi

from bot import settings


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


def save_msg( f):
    @wraps(f)
    def save(api: TelegramBotApi, update):
        Message.from_update(api, update)
        return f(api, update)

    return save


def with_user( f):
    @wraps(f)
    def get_user(api: TelegramBotApi, update):
        user = api.get_user(update.message.chat_id)
        return f(api, user, update)

    return get_user


def rhandler(text, callback):
    return RegexHandler('^({})$'.format(text), callback)