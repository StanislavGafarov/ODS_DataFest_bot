import time
from functools import wraps

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import MessageHandler, Filters, run_async, ConversationHandler, CommandHandler, RegexHandler

from backend.models import Message, Invite, TGUser, Event
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.utils import logger
from backend.get_google_files import GoogleSpreadsheet


class TGHandlers():
    def __init__(self):
        self.gss_client = GoogleSpreadsheet(client_secret_path='')
        self.CHOOSING = 0
        self.CHECK_EMAIL = 1
        self.BROADCAST = 2
        self.SCHEDULE = 3

        self.NOT_REGISTERED_KEYBOARD = [[BUTTON_CHECK_EMAIL, BUTTON_SHEDULE, BUTTON_REGISTRATION]]
        self.SHEDULE_KEYBOARD = [[BUTTON_10_MAY_SHEDULE, BUTTON_11_MAY_SHEDULE]]

        self.ADMIN_KEYBOARD = [[BUTTON_CHECK_EMAIL, BUTTON_SHEDULE, BUTTON_REGISTRATION, BUTTON_CREATE_BROADCAST]]

    def kb(self, user: TGUser):
        return ReplyKeyboardMarkup(self.ADMIN_KEYBOARD if user.is_admin else self.NOT_REGISTERED_KEYBOARD
                                   , one_time_keyboard=True)

    @staticmethod
    def save_msg(f):
        @wraps(f)
        def save(api: TelegramBotApi, update):
            Message.from_update(api, update)
            return f(api, update)

        return save

    @staticmethod
    def with_user(f):
        @wraps(f)
        def get_user(api: TelegramBotApi, update):
            user = api.get_user(update.message.chat_id)
            return f(api, user, update)

        return get_user

    @run_async
    @save_msg
    @with_user
    def menu(self, api: TelegramBotApi, user: TGUser, update):
        logger.info('User {} have started conversation.'.format(user))
        update.message.reply_text(
            TEXT_HELLO,
            reply_markup=self.kb(user))

        return self.CHOOSING

    @run_async
    @save_msg
    @with_user
    def check_email(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_ENTER_EMAIL,
                                  reply_markup=ReplyKeyboardRemove())
        return self.CHECK_EMAIL

    @run_async
    @save_msg
    @with_user
    def email_in_list(self, api: TelegramBotApi, user: TGUser, update):
        email = update.message.text
        logger.info('{}'.format(email))
        if Invite.objects.filter(email=email).first() is not None:
            update.message.reply_text(TEXT_EMAIL_OK,
                                      reply_markup=self.kb(user))
        else:
            update.message.reply_text(TEXT_EMAIL_NOT_OK,
                                      reply_markup=self.kb(user))

        if user.last_checked_email != email:
            user.is_notified = False  # todo ????
            user.last_checked_email = email
            user.save()
        return self.CHOOSING

    @run_async
    @save_msg
    @with_user
    def show_schedule(self, api: TelegramBotApi, user: TGUser, update):

        custom_keyboard = ReplyKeyboardMarkup(self.SHEDULE_KEYBOARD, one_time_keyboard=True)
        update.message.reply_text(TEXT_SHOW_SCHEDULE
                                  , reply_markup=custom_keyboard)
        return self.SCHEDULE

    @run_async
    @save_msg
    @with_user
    def schedule_day(self, api: TelegramBotApi, user: TGUser, update):
        day_table = self.gss_client.get_data('SCHEDULE_TEST')
        update.message.reply_text('{}'.format(day_table.to_string(index=False))
                                  , reply_markup=self.kb(user))
        return self.CHOOSING

    @run_async
    @save_msg
    @with_user
    def can_spam(self, api: TelegramBotApi, user: TGUser, update):
        user.is_subscribed = True
        user.save()
        logger.info('{} subscribed for notification'.format(user))
        update.message.reply_text(TEXT_AFTER_SUB,
                                  reply_markup=self.kb(user))
        return self.CHOOSING

    @run_async
    @save_msg
    @with_user
    def skip_email(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s did not send an email.", user)
        update.message.reply_text(TEXT_SKIP_EMAIL, reply_markup=self.kb(user))
        return self.CHOOSING

    @run_async
    @save_msg
    @with_user
    def create_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s initiated broadcast.", user)
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=kb(user))
        update.message.reply_text(TEXT_ENTER_BROADCAST)
        return self.BROADCAST

    @run_async
    @save_msg
    @with_user
    def send_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        broadcast_text = update.message.text
        for u in TGUser.objects.all():
            try:
                api.bot.send_message(u.tg_id, broadcast_text)
                time.sleep(.1)
            except:
                logger.exception('Error sending broadcast to user {}'.format(u))
        update.message.reply_text(TEXT_BROADCAST_DONE, reply_markup=self.kb(user))

    @run_async
    @save_msg
    @with_user
    def cancel(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s canceled the conversation.", user)
        update.message.reply_text(TEXT_BYE,
                                  reply_markup=ReplyKeyboardRemove())

    def rhandler(self, text, callback):
        return RegexHandler('^({})$'.format(text), callback)

    def get_handlers(self):
        handlers = [
            ConversationHandler(
                entry_points=[CommandHandler('start', self.menu)],

                states={
                    self.CHOOSING: [
                        self.rhandler(BUTTON_CHECK_EMAIL, self.check_email),
                        self.rhandler(BUTTON_SHEDULE, self.show_schedule),
                        self.rhandler(BUTTON_REGISTRATION, self.can_spam),
                        self.rhandler(BUTTON_CREATE_BROADCAST, self.create_broadcast)
                    ],

                    self.SCHEDULE:[
                        self.rhandler(BUTTON_10_MAY_SHEDULE, self.schedule_day),
                        self.rhandler(BUTTON_11_MAY_SHEDULE, self.schedule_day)
                    ],

                    self.CHECK_EMAIL: [MessageHandler(Filters.text, self.email_in_list),
                                  CommandHandler('skip', self.skip_email)],

                    self.BROADCAST: [MessageHandler(Filters.text, self.send_broadcast),
                                CommandHandler('skip', self.skip_email)]  # fixme
                },

                fallbacks=[CommandHandler('cancel', self.cancel)]
            )
        ]
        return handlers

