from telegram.ext import run_async, MessageHandler, Filters

from backend.tgbot.tghandler import TGHandler
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.utils import Decorators, logger
from backend.models import TGUser
from backend.tgbot.texts import *

class GetNews(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def subscribe_for_news(self, api: TelegramBotApi, user: TGUser, update):
        user.is_notified = True
        user.save()
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NEWS_SUBSCRIBED, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def unsubscribe_for_news(self, api: TelegramBotApi, user: TGUser, update):
        user.is_notified = False
        user.save()
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NEWS_UNSUBSCRIBED, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def get_last_5_news(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    def create_state(self):
        state = {self.GET_NEWS: [
            self.rhandler(BUTTON_NEWS_UNSUBSCRIPTION, self.unsubscribe_for_news),
            self.rhandler(BUTTON_NEWS_SUBSCRIPTION, self.subscribe_for_news),
            self.rhandler(BUTTON_GET_LAST_5_NEWS, self.not_ready_yet),
            self.rhandler(BUTTON_FULL_BACK, self.full_back),
            MessageHandler(Filters.text, self.unknown_command)
        ]}
        return state