from telegram.ext import run_async, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardRemove
from django.core.paginator import Paginator

from backend.tgbot.tghandler import TGHandler
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.utils import Decorators, logger
from backend.models import TGUser, News, NewsGroup
from backend.tgbot.texts import *

class GetNews(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def subscribe_for_news(self, api: TelegramBotApi, user: TGUser, update):
        user.has_news_subscription = True
        user.save()
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NEWS_SUBSCRIBED, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def unsubscribe_for_news(self, api: TelegramBotApi, user: TGUser, update):
        user.has_news_subscription = False
        user.save()
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NEWS_UNSUBSCRIBED, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def show_news(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        news_list = News.object.filter(target_group=NewsGroup.news_subscription())
        news_pages = Paginator(news_list, 1)
        page = news_pages.get_page(1)

        keyboard = [[BUTTON_NEWS_UNSUBSCRIPTION,BUTTON_FULL_BACK, BUTTON_NEWS_MORE]]
        for news in page:
            send = news.get_sender()
            send(api, user, reply_markup=keyboard)

        return self.GET_NEWS

    def create_state(self):
        state = {self.GET_NEWS: [
            self.rhandler(BUTTON_NEWS_UNSUBSCRIPTION, self.unsubscribe_for_news),
            self.rhandler(BUTTON_NEWS_SUBSCRIPTION, self.subscribe_for_news),
            self.rhandler(BUTTON_GET_LAST_5_NEWS, self.show_news),
            self.rhandler(BUTTON_NEWS_MORE, self.show_news),
            self.rhandler(BUTTON_FULL_BACK, self.full_back),
            CallbackQueryHandler(callback=self.render_news, pattern="news_page\?\d*"),
            MessageHandler(Filters.text, self.unknown_command)
        ]}
        return state