import time
from threading import Thread

from telegram.ext import run_async, MessageHandler, Filters, CommandHandler

from backend.models import TGUser
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.tghandler import TGHandler
from backend.tgbot.utils import Decorators, logger


class BroadcastThread(Thread):
    def __init__(self, api, user, text):
        super().__init__()
        self.user = user
        self.api = api
        self.text = text

    def run(self):
        # TODO spam only for is_notified
        counter = 0
        error_counter = 0
        for u in TGUser.objects.all():
            try:
                self.api.bot.send_message(u.tg_id, self.text)
                time.sleep(.1)
                counter += 1
            except:
                logger.exception('Error sending broadcast to user {}'.format(u))
                error_counter += 1
        self.api.bot.send_message(self.user.tg_id, TEXT_BROADCAST_DONE.format(counter, error_counter))


class Broadcasting(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def send_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        bc = BroadcastThread(api, user, update.message.text)
        bc.start()
        update.message.reply_text(TEXT_BROADCAST_STARTED, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def cancel_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User {} desided not to send broadcast.", user)
        update.message.reply_text(TEXT_CANCEL_BROADCASTING,
                                  reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    def create_state(self):
        state = {self.BROADCAST: [MessageHandler(Filters.text, self.send_broadcast),
                                  CommandHandler('cancel', self.cancel_broadcast)]}
        return state
