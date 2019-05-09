from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import run_async, ConversationHandler, RegexHandler

from backend.models import TGUser, RandomBeerUser
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.utils import logger, Decorators

from concurrent.futures.thread import ThreadPoolExecutor


_thread_pool = ThreadPoolExecutor(max_workers=4)


class TGHandler(object):
    def __init__(self):
        self.MAIN_MENU = 0
        self.CHECK_REGISTRATION_STATUS = 1
        self.AUTHORIZATION = 2
        self.CHECK_CODE = 21
        self.GET_NEWS = 3

        self.CHOOSEN_SIZE = 40
        self.CHANGE_SIZE = 41

        self.RANDOM_BEER_MENU = 42
        self.RANDOM_BEER_RULES = 43
        self.RANDOM_BEER_TG_NICK = 44
        self.RANDOM_BEER_ODS_NICK = 45
        self.RANDOM_BEER_SN_LINK = 46
        self.RANDOM_BEER_CHANGE_FIELD = 47

        self.NVIDIA_JETSON = 101
        self.DRAW_JETSON = 102

        # self.ON_MAJOR = 100


        # Admin
        self.BROADCAST = 995
        self.BROADCAST_TYPE_MESSAGE = 996
        self.DRAW_PRIZES = 997

        admin_buttons = [
            [BUTTON_REFRESH_SCHEDULE],
            [BUTTON_SEND_INVITES],
            [BUTTON_DRAW_PRIZES],
            [BUTTON_POST_NEWS],
            [BUTTON_DRAW_JETSON]
        ]
        auth_buttons = [
            # [BUTTON_ON_MAJOR],
            [BUTTON_SCHEDULE],
            [BUTTON_NEWS,
             BUTTON_SHOW_PATH],
            [BUTTON_PARTICIPATE_IN_RANDOM_PRIZE],
            [BUTTON_JETSON]
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
                              [BUTTON_XL_SIZE, BUTTON_XXL_SIZE, BUTTON_FULL_BACK]]

        self.RANDOM_BEER_MENU_KEYBOARD = [[BUTTON_CHANGE_TG_NICK],
                                          [BUTTON_CHANGE_ODS_NICK],
                                          [BUTTON_CHANGE_SN_LINK]]

        self.BROADCAST_SELECT_GROUP_KEYBOARD = [[BUTTON_NEWS_GROUP_WITH_SUBSCRIPTION],
                                                [BUTTON_NEWS_GROUP_ADMIN],
                                                # [BUTTON_NEWS_GROUP_WINNERS],
                                                [BUTTON_NEWS_GROUP_ALL],
                                                [BUTTON_FULL_BACK]]

        self.ADMIN_KEYBOARD = admin_buttons + auth_buttons
        self.AUTHORIZED_USER_KEYBOARD = auth_buttons
        self.UNAUTHORIZED_USER_KEYBOARD = unauth_buttons

    @staticmethod
    def add_task(task, *args, **kwargs):
        def wrap(*args, **kwargs):
            try:
                task(*args, **kwargs)
            except:
                logger.exception(f'Error while running task {task}')

        _thread_pool.submit(wrap, *args, **kwargs)

    def define_keyboard(self, user: TGUser):
        if user.is_admin:
            keyboard = self.ADMIN_KEYBOARD
        elif user.is_authorized:
            keyboard = self.AUTHORIZED_USER_KEYBOARD
        else:
            keyboard = self.UNAUTHORIZED_USER_KEYBOARD
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    def random_beer_keyboard(self, random_beer_user: RandomBeerUser):
        if random_beer_user.is_busy:
            keyboard = self.RANDOM_BEER_MENU_KEYBOARD + [[BUTTON_END_MEETING], [BUTTON_FULL_BACK]]
        else:
            keyboard = self.RANDOM_BEER_MENU_KEYBOARD + [[BUTTON_FIND_MATCH], [BUTTON_FULL_BACK]]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    def broadcast_group_keyboard(self, user: TGUser):
        if user.is_admin:
            keyboard = self.BROADCAST_SELECT_GROUP_KEYBOARD
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
