import time

from telegram.ext import run_async, MessageHandler, Filters, CommandHandler

from backend.tgbot.tghandler import TGHandler
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.utils import Decorators, logger
from backend.models import TGUser
from backend.tgbot.texts import *

class Broadcasting(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def send_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        # TODO spam only for is_notified
        broadcast_text = update.message.text
        for u in TGUser.objects.all():
            try:
                api.bot.send_message(u.tg_id, broadcast_text)
                time.sleep(.1)
            except:
                logger.exception('Error sending broadcast to user {}'.format(u))
        update.message.reply_text(TEXT_BROADCAST_DONE, reply_markup=self.define_keyboard(user))
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