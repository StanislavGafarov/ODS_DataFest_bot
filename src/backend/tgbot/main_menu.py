from telegram import ReplyKeyboardRemove
from telegram.ext import run_async, MessageHandler, Filters

from backend.tgbot.utils import logger, Decorators
from backend.tgbot.handlers_new import TGHandler
from backend.tgbot.base import TelegramBotApi
from backend.models import Invite, TGUser
from backend.tgbot.texts import *


class MainMenu(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def check_registration_status(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_ENTER_EMAIL, reply_markup=ReplyKeyboardRemove())
        return self.CHECK_REGISTRATION_STATUS

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def authorization(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_ENTER_EMAIL, reply_markup=ReplyKeyboardRemove())
        return self.AUTHORIZATION

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def get_news(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        if user.is_notified:
            custom_keyboard = [[BUTTON_NEWS_UNSUBSCRIPTION,
                                BUTTON_FULL_BACK
                                # BUTTON_GET_LAST_5_NEWS
                                ]]
        else:
            custom_keyboard = [[BUTTON_NEWS_SUBSCRIPTION,
                                BUTTON_FULL_BACK
                                # BUTTON_GET_LAST_5_NEWS
                                ]]
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NEWS, reply_markup=ReplyKeyboardMarkup(custom_keyboard
                                                                              , one_time_keyboard=True
                                                                              , resize_keyboard=True))
        return self.GET_NEWS

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def not_ready_yet(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def get_schedule(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def show_path(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    # @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    # def who_is_your_daddy(self, api: TelegramBotApi, user: TGUser, update):
    #     return self.MAIN_MENU  # Nope
    #     text = update.message.text
    #     logger.info('User {} have chosen {} '.format(user, text))
    #     if user.is_admin:
    #         user.is_admin = False
    #         user.save()
    #         update.message.reply_text('God mode :off', reply_markup=self.define_keyboard(user))
    #     else:
    #         user.is_admin = True
    #         user.save()
    #         update.message.reply_text('God mode :on', reply_markup=self.define_keyboard(user))
    #     return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def unknown_command(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} wrote unknown command: {}'.format(user, text))
        update.message.reply_text(TEXT_UNKNOWN_COMMAND, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    def create_states(self):
        states = {self.MAIN_MENU: [
            self.rhandler(BUTTON_CHECK_REGISTRATION, self.check_registration_status),
            self.rhandler(BUTTON_AUTHORISATION, self.authorization),
            self.rhandler(BUTTON_NEWS, self.get_news),
            self.rhandler(BUTTON_SCHEDULE, self.get_schedule),
            self.rhandler(BUTTON_SHOW_PATH, self.show_path),

            self.rhandler(BUTTON_PARTICIPATE_IN_RANDOM_PRIZE, self.not_ready_yet),
            self.rhandler(BUTTON_RANDOM_BEER, self.not_ready_yet),

            self.rhandler(BUTTON_REFRESH_SCHEDULE, self.not_ready_yet),
            self.rhandler(BUTTON_SEND_INVITES, self.refresh_invites_and_notify),
            self.rhandler(BUTTON_START_RANDOM_PRIZE, self.not_ready_yet),
            self.rhandler(BUTTON_POST_NEWS, self.create_broadcast),

            # self.rhandler('88224646BA', self.who_is_your_daddy),

            # self.rhandler(BUTTON_SHEDULE, self.show_schedule),

            # self.rhandler(BUTTON_CREATE_BROADCAST, self.create_broadcast)
            MessageHandler(Filters.text, self.unknown_command)
        ]}
        return states