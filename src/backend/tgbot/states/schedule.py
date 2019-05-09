import random
import requests
import time
from telegram import ReplyKeyboardMarkup
from telegram.ext import run_async, MessageHandler, Filters
from telegram.error import Unauthorized

from backend.tgbot.tghandler import TGHandler
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.utils import Decorators, logger
from backend.models import TGUser, Event
from backend.tgbot.texts import *


class Schedule(TGHandler):
    @staticmethod
    def update_schedule():
        schedule_url = "https://datafest.ru/static/data/speakers.txt"
        try:
            response = requests.request('GET', schedule_url, timeout=5)
            if not response:
                class EmptyResponse(Exception):
                    pass

                raise EmptyResponse
            event_data = response.json()['data']
        except:
            logger.exception('Schedule update failed.')
            return
        Event.objects.all().delete()
        for data in event_data:
            event = Event.from_json(data)
            event.save()
        return True
