from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import run_async, ConversationHandler, RegexHandler

from backend.models import TGUser
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.utils import logger, Decorators


class TGHandler(object):
    def __init__(self):
        self.MAIN_MENU = 0
        self.CHECK_REGISTRATION_STATUS = 1
        self.AUTHORIZATION = 2
        self.CHECK_CODE = 21
        self.GET_NEWS = 3

        # self.FREE_PRIZES = 41
        self.CHOOSEN_SIZE = 41
        self.CHANGE_SIZE = 42

        # Admin
        self.BROADCAST = 995
        self.DRAW_PRIZES = 996

        admin_buttons = [
            [BUTTON_REFRESH_SCHEDULE],
            [BUTTON_SEND_INVITES],
            [BUTTON_DRAW_PRIZES],
            [BUTTON_POST_NEWS]
        ]
        auth_buttons = [
            [BUTTON_SCHEDULE],
            [BUTTON_NEWS,
             BUTTON_SHOW_PATH],
            [BUTTON_PARTICIPATE_IN_RANDOM_PRIZE],
            [BUTTON_RANDOM_BEER]
        ]
        unauth_buttons = [
            [BUTTON_CHECK_REGISTRATION],
            [BUTTON_AUTHORISATION],
            [BUTTON_SCHEDULE,
             BUTTON_NEWS],
            [BUTTON_SHOW_PATH]
        ]
        self.SIZE_KEYBOARD = [[BUTTON_XS_SIZE, BUTTON_S_SIZE, BUTTON_M_SIZE, BUTTON_L_SIZE],
                              [BUTTON_XL_SIZE, BUTTON_XXL_SIZE, BUTTON_XXXL_SIZE, BUTTON_FULL_BACK]]

        self.ADMIN_KEYBOARD = admin_buttons + unauth_buttons
        self.AUTHORIZED_USER_KEYBOARD = auth_buttons
        self.UNAUTHORIZED_USER_KEYBOARD = unauth_buttons

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

    # START
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def start(self, api: TelegramBotApi, user: TGUser, update):
        logger.info('User {} have started conversation.'.format(user))
        update.message.reply_text(
            TEXT_HELLO,
            reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    # Some usefull functions
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def skip_email(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s did not send an email.", user)
        update.message.reply_text(TEXT_SKIP_EMAIL, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def not_ready_yet(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def unknown_command(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} wrote unknown command: {}'.format(user, text))
        update.message.reply_text(TEXT_UNKNOWN_COMMAND, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def full_back(self, api:TelegramBotApi, user:TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_FULL_BACK, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    # END
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def cancel(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User %s canceled the conversation.", user)
        update.message.reply_text(TEXT_BYE,
                                  reply_markup=ReplyKeyboardRemove())

    def create_state(self):
        return NotImplementedError


def restore_states(conv_handler: ConversationHandler):
    # hacky way to restore conversations
    logger.info('restoring user states')
    for user in TGUser.objects.exclude(state=None).all():
        if user.state is not None:
            key = (user.tg_id, user.tg_id)
            conv_handler.conversations[key] = user.state
    logger.info('restoring done')
