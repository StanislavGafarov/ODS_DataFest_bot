import time
from functools import wraps
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import MessageHandler, Filters, run_async, ConversationHandler, CommandHandler, RegexHandler
from backend.models import Message, Invite, TGUser, Event
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.utils import logger
from backend.google_spreadsheet_client import GoogleSpreadsheet


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
            return f(cls, api, user, update)

        return get_user

    def composed(*decs):
        def deco(f):
            for dec in reversed(decs):
                f = dec(f)
            return f

        return deco


class TGHandlers():
    def __init__(self):
        self.gss_client = GoogleSpreadsheet(client_secret_path='./backend/tgbot/client_secret.json')
        self.CHOOSING = 0
        self.CHECK_EMAIL = 1
        self.BROADCAST = 2
        self.SCHEDULE = 3
        self.ADMIN_KEYBOARD = [[BUTTON_REFRESH_SCHEDULE, BUTTON_SEND_INVITES, BUTTON_START_RANDOM_PRIZE, BUTTON_POST_NEWS]]
        self.AUTHORIZED_USER_KEYBOARD = [[BUTTON_SCHEDULE, BUTTON_NEWS, BUTTON_SHOW_PATH,
                                    BUTTON_PARTICIPATE_IN_RANDOM_PRIZE, BUTTON_RANDOM_BEER]]
        self.UNAUTHORIZED_USER_KEYBOARD = [[BUTTON_CHECK_REGISTRATION, BUTTON_AUTHORISATION, BUTTON_SCHEDULE,
                                      BUTTON_NEWS, BUTTON_SHOW_PATH]]

    def define_keyboard(self, user: TGUser):
        if user.is_admin:
            keyboard = self.ADMIN_KEYBOARD
        elif user.is_authorized:
            keyboard = self.AUTHORIZED_USER_KEYBOARD
        else:
            keyboard = self.UNAUTHORIZED_USER_KEYBOARD
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    def rhandler(self, text, callback):
        return RegexHandler('^({})$'.format(text), callback)

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def menu(self, api: TelegramBotApi, user: TGUser, update):
        logger.info('User {} have started conversation.'.format(user))
        update.message.reply_text(
            TEXT_HELLO,
            reply_markup=self.kb(user))
        return self.CHOOSING

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def check_email(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_ENTER_EMAIL,
                                  reply_markup=ReplyKeyboardRemove())
        return self.CHECK_EMAIL

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def email_in_list(self, api: TelegramBotApi, user: TGUser, update):
        email = update.message.text
        logger.info('{}'.format(email))
        if Invite.objects.filter(email=email).first() is not None:
            update.message.reply_text(TEXT_EMAIL_OK,
                                      reply_markup=self.define_keyboard(user))
        else:
            update.message.reply_text(TEXT_EMAIL_NOT_OK,
                                      reply_markup=self.define_keyboard(user))
        if user.last_checked_email != email:
            user.is_notified = False  # todo ????
            user.last_checked_email = email
            user.save()
        return self.CHOOSING

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def show_schedule(self, api: TelegramBotApi, user: TGUser, update):
        custom_keyboard = ReplyKeyboardMarkup(self.SHEDULE_KEYBOARD, one_time_keyboard=True)
        update.message.reply_text(TEXT_SHOW_SCHEDULE
                                  , reply_markup=custom_keyboard)
        return self.SCHEDULE

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def schedule_day(self, api: TelegramBotApi, user: TGUser, update):
        day_table = self.gss_client.get_data('SCHEDULE_TEST')
        update.message.reply_text('{}'.format(day_table.to_string(index=False))
                                  , reply_markup=self.define_keyboard(user))
        return self.CHOOSING

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def can_spam(self, api: TelegramBotApi, user: TGUser, update):
        user.is_subscribed = True
        user.save()
        logger.info('{} subscribed for notification'.format(user))
        update.message.reply_text(TEXT_AFTER_SUB,
                                  reply_markup=self.define_keyboard(user))
        return self.CHOOSING

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def skip_email(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s did not send an email.", user)
        update.message.reply_text(TEXT_SKIP_EMAIL, reply_markup=self.define_keyboard(user))
        return self.CHOOSING

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def create_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s initiated broadcast.", user)
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
        update.message.reply_text(TEXT_ENTER_BROADCAST)
        return self.BROADCAST

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def send_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        broadcast_text = update.message.text
        for u in TGUser.objects.all():
            try:
                api.bot.send_message(u.tg_id, broadcast_text)
                time.sleep(.1)
            except:
                logger.exception('Error sending broadcast to user {}'.format(u))
        update.message.reply_text(TEXT_BROADCAST_DONE, reply_markup=self.define_keyboard(user))

    @Decorators.composed(run_async, Decorators.with_user, Decorators.save_msg)
    # @run_async
    # @Decorators.main_decorator
    def cancel(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s canceled the conversation.", user)
        update.message.reply_text(TEXT_BYE,
                                  reply_markup=ReplyKeyboardRemove())

    def get_handlers(self):
        handlers = [
            ConversationHandler(
                entry_points=[CommandHandler('start', self.menu)],
                states={
                    self.CHOOSING: [
                        self.rhandler(BUTTON_CHECK_EMAIL, self.check_email),
                        # self.rhandler(BUTTON_SHEDULE, self.show_schedule),
                        self.rhandler(BUTTON_REGISTRATION, self.can_spam),
                        # self.rhandler(BUTTON_CREATE_BROADCAST, self.create_broadcast)
                    ],
                    # self.SCHEDULE: [
                    #     self.rhandler(BUTTON_10_MAY_SHEDULE, self.schedule_day),
                    #     self.rhandler(BUTTON_11_MAY_SHEDULE, self.schedule_day)
                    # ],
                    self.CHECK_EMAIL: [MessageHandler(Filters.text, self.email_in_list),
                                       CommandHandler('skip', self.skip_email)],
                    self.BROADCAST: [MessageHandler(Filters.text, self.send_broadcast),
                                     CommandHandler('skip', self.skip_email)]  # fixme
                },
                fallbacks=[CommandHandler('cancel', self.cancel)]
            )
        ]
        return handlers