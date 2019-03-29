import time
import traceback

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import MessageHandler, Filters, run_async, ConversationHandler, CommandHandler, RegexHandler

from backend.google_spreadsheet_client import GoogleSpreadsheet
from backend.models import Invite, TGUser
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.utils import logger, Decorators


class TGHandlers(object):
    def __init__(self):
        self.gss_client = GoogleSpreadsheet(client_secret_path='./backend/tgbot/client_secret.json')
        self.MAIN_MENU = 0
        self.CHECK_REGISTRATION_STATUS = 1
        self.AUTHORIZATION = 2
        self.CHECK_CODE = 99
        self.GET_NEWS = 3

        self.CHECK_EMAIL = 4
        self.BROADCAST = 5

        admin_buttons = [
            BUTTON_REFRESH_SCHEDULE,
            BUTTON_SEND_INVITES,
            BUTTON_START_RANDOM_PRIZE,
            BUTTON_POST_NEWS
        ]
        auth_buttons = [
            BUTTON_SCHEDULE,
            BUTTON_NEWS,
            BUTTON_SHOW_PATH,
            BUTTON_PARTICIPATE_IN_RANDOM_PRIZE,
            BUTTON_RANDOM_BEER
        ]
        # UNAUTH_ONLY_BUTTONS = []
        unauth_buttons = [
            BUTTON_CHECK_REGISTRATION,
            BUTTON_AUTHORISATION,
            BUTTON_SCHEDULE,
            # BUTTON_NEWS,
            BUTTON_SHOW_PATH
        ]
        self.ADMIN_KEYBOARD = [admin_buttons, unauth_buttons]
        self.AUTHORIZED_USER_KEYBOARD = [auth_buttons]
        self.UNAUTHORIZED_USER_KEYBOARD = [unauth_buttons]

    def define_keyboard(self, user: TGUser):
        if user.is_admin:
            keyboard = self.ADMIN_KEYBOARD
        elif user.is_authorized:
            keyboard = self.AUTHORIZED_USER_KEYBOARD
        else:
            keyboard = self.UNAUTHORIZED_USER_KEYBOARD
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    def rhandler(self, text, callback):
        return RegexHandler('^({})$'.format(text), callback)

    ######## MONKEY CODE STARTED HERE ########

    # START
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def start(self, api: TelegramBotApi, user: TGUser, update):
        logger.info('User {} have started conversation.'.format(user))
        update.message.reply_text(
            TEXT_HELLO,
            reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    # MAIN MENU
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
                                # BUTTON_GET_LAST_5_NEWS
                                ]]
        else:
            custom_keyboard = [[BUTTON_NEWS_SUBSCRIPTION,
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

    ## CHECK_REGISTRATION_STATUS
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
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
            user.last_checked_email = email
            user.save()
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def skip_email(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s did not send an email.", user)
        update.message.reply_text(TEXT_SKIP_EMAIL, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    ## AUTHORIZATION
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def auth_check_email(self, api: TelegramBotApi, user: TGUser, update):
        email = update.message.text
        logger.info('{}'.format(email))
        if Invite.objects.filter(email=email).first() is not None:
            update.message.reply_text(TEXT_AUTH_EMAIL_OK, reply_markup=ReplyKeyboardRemove())
        else:
            update.message.reply_text(TEXT_EMAIL_NOT_OK,
                                      reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU

        if user.last_checked_email != email:
            user.last_checked_email = email
            user.save()
        return self.CHECK_CODE

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def auth_check_code(self, api: TelegramBotApi, user: TGUser, update):
        code = update.message.text
        try:
            code = int(code)
        except:
            code = None
        if code is not None and Invite.objects.filter(email=user.last_checked_email, code=code):
            user.is_authorized = True
            user.save()
            update.message.reply_text(TEXT_CODE_OK,
                                      reply_markup=self.define_keyboard(user))
        else:
            update.message.reply_text(TEXT_CODE_NOT_OK,
                                      reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    ## GET NEWS
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

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def check_email(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_ENTER_EMAIL,
                                  reply_markup=ReplyKeyboardRemove())
        return self.CHECK_EMAIL

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def create_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s initiated broadcast.", user)
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
        update.message.reply_text(TEXT_ENTER_BROADCAST)
        return self.BROADCAST

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
    def cancel(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s canceled the conversation.", user)
        update.message.reply_text(TEXT_BYE,
                                  reply_markup=ReplyKeyboardRemove())

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def cancel_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User {} desided not to send broadcast.", user)
        update.message.reply_text(TEXT_CANCEL_BROADCASTING,
                                  reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    ### ADMIN
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def refresh_invites_and_notify(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s initiated invites refresh.", user)
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
        update.message.reply_text(TEXT_START_INVITE_REFRESH)
        try:
            new_invites_count = self.gss_client.update_invites()
            update.message.reply_text(TEXT_REPORT_INVITE_COUNT.format(new_invites_count))
            notification_count = send_notifications(api)
            update.message.reply_text(TEXT_REPORT_NOTIFICATION_COUNT.format(notification_count),
                                      reply_markup=self.define_keyboard(user))
        except:
            update.message.reply_text(TEXT_REPORT_INVITE_REFRESH_ERROR + '\n' + traceback.format_exc(),
                                      reply_markup=self.define_keyboard(user))
            logger.exception('error updating invites')
        return self.MAIN_MENU

    def get_handlers(self):
        handlers = [
            ConversationHandler(
                entry_points=[CommandHandler('start', self.start)],
                states={
                    self.MAIN_MENU: [
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

                        self.rhandler(BUTTON_CHECK_EMAIL, self.check_email),
                        # self.rhandler(BUTTON_SHEDULE, self.show_schedule),

                        # self.rhandler(BUTTON_CREATE_BROADCAST, self.create_broadcast)
                        MessageHandler(Filters.text, self.unknown_command)
                    ],

                    self.CHECK_REGISTRATION_STATUS: [
                        MessageHandler(Filters.text, self.email_in_list),
                        CommandHandler('skip', self.skip_email)
                    ],

                    self.AUTHORIZATION: [MessageHandler(Filters.text, self.auth_check_email),
                                         CommandHandler('skip', self.skip_email)
                    ],
                    self.CHECK_CODE: [MessageHandler(Filters.text, self.auth_check_code)],

                    self.GET_NEWS: [
                        self.rhandler(BUTTON_NEWS_UNSUBSCRIPTION, self.unsubscribe_for_news),
                        self.rhandler(BUTTON_NEWS_SUBSCRIPTION, self.subscribe_for_news),
                        self.rhandler(BUTTON_GET_LAST_5_NEWS, self.not_ready_yet),
                        MessageHandler(Filters.text, self.unknown_command)
                    ],

                    self.CHECK_EMAIL: [MessageHandler(Filters.text, self.email_in_list),
                                       CommandHandler('skip', self.skip_email)],
                    self.BROADCAST: [MessageHandler(Filters.text, self.send_broadcast),
                                     CommandHandler('cancel', self.cancel_broadcast)]
                },
                fallbacks=[CommandHandler('cancel', self.cancel)]
            )
        ]
        return handlers


def send_notifications(api: TelegramBotApi):
    count = 0

    for user in TGUser.objects.filter(is_notified=False).exclude(last_checked_email='').all():
        invite = Invite.objects.filter(email=user.last_checked_email).first()
        if invite is not None:
            api.bot.send_message(user.tg_id, TEXT_INVITE_NOTIFICATION)
            user.is_notified = True
            user.save()
            count += 1
    return count
