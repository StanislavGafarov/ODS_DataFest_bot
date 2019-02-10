import logging
import os

import requests

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
