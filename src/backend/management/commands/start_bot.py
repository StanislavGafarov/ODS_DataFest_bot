import logging
import sys

from django.core.management.base import BaseCommand

from backend.tgbot.handlers import MainHandler
from backend.tgbot.sync_api import SyncBotApi
from backend.tgbot.utils import logger
from bot import settings


class Command(BaseCommand):
    help = 'Run Bot'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--token', default=None)
        parser.add_argument('-d', '--debug', action='store_true')

    def handle(self, *args, **options):
        if options['debug']:
            tglogger = logging.getLogger("telegram")
            tglogger.setLevel(level=logging.DEBUG)
            tglogger.addHandler(logging.StreamHandler(sys.stdout))
        if options['token'] is None:
            token = settings.DEFAULT_BOT_TOKEN
        else:
            token = options['token']
        logger.info('Using token {}'.format(token))
        mh = MainHandler()
        SyncBotApi(token).start_bot(mh.get_handlers())
