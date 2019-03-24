import time

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import MessageHandler, Filters, run_async, ConversationHandler, CommandHandler

from backend.models import Invite, TGUser
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.utils import logger, save_msg, with_user, rhandler
from backend.google_spreadsheet_client import GoogleSpreadsheet
from backend.tgbot.states.main_menu import make_keyboard
from backend.tgbot.states.main_menu import MAIN_MENU, check_registration_status, authorization


GSS_CLIENT = GoogleSpreadsheet(client_secret_path='./backend/tgbot/client_secret.json')

# MAIN_MENU = 1
CHECK_REGISTRATION_STATUS = 2
AUTHORIZATION = 3
BROADCAST = 4
SCHEDULE = 5
CHECK_EMAIL = 6


NOT_REGISTERED_KEYBOARD = [[BUTTON_CHECK_EMAIL, BUTTON_SCHEDULE, BUTTON_REGISTRATION]]
SHEDULE_KEYBOARD = [[BUTTON_10_MAY_SCHEDULE, BUTTON_11_MAY_SCHEDULE]]

ADMIN_KEYBOARD = [[BUTTON_CHECK_EMAIL, BUTTON_SCHEDULE, BUTTON_REGISTRATION, BUTTON_POST_NEWS]]


def kb(user: TGUser):
    return ReplyKeyboardMarkup(ADMIN_KEYBOARD if user.is_admin else NOT_REGISTERED_KEYBOARD
                               , one_time_keyboard=True)

@run_async
@save_msg
@with_user
def start(api: TelegramBotApi, user: TGUser, update):
    logger.info('User {} have started conversation.'.format(user))
    update.message.reply_text(
        TEXT_HELLO,
        reply_markup=kb(user))

    return MAIN_MENU



@run_async
@save_msg
@with_user
def check_email(api: TelegramBotApi, user: TGUser, update):
    email = update.message.text
    logger.info('{}'.format(email))
    if Invite.objects.filter(email=email).first() is not None:
        update.message.reply_text(TEXT_EMAIL_OK,
                                  reply_markup=kb(user))
    else:
        update.message.reply_text(TEXT_EMAIL_NOT_OK,
                                  reply_markup=kb(user))

    if user.last_checked_email != email:
        user.is_notified = False  # todo ????
        user.last_checked_email = email
        user.save()
    return MAIN_MENU

@run_async
@save_msg
@with_user
def skip_email(api: TelegramBotApi, user: TGUser, update):
    logger.info("User %s did not send an email.", user)
    update.message.reply_text(TEXT_SKIP_EMAIL, reply_markup=make_keyboard(user))
    return MAIN_MENU

@run_async
@save_msg
@with_user
def show_schedule(api: TelegramBotApi, user: TGUser, update):

    custom_keyboard = ReplyKeyboardMarkup(SHEDULE_KEYBOARD, one_time_keyboard=True)
    update.message.reply_text(TEXT_SHOW_SCHEDULE
                              , reply_markup=custom_keyboard)
    return SCHEDULE

@run_async
@save_msg
@with_user
def schedule_day(api: TelegramBotApi, user: TGUser, update):
    day_table = GSS_CLIENT.get_data('SCHEDULE_TEST')
    update.message.reply_text('{}'.format(day_table.to_string(index=False))
                              , reply_markup=kb(user))
    return MAIN_MENU

@run_async
@save_msg
@with_user
def can_spam(api: TelegramBotApi, user: TGUser, update):
    user.is_subscribed = True
    user.save()
    logger.info('{} subscribed for notification'.format(user))
    update.message.reply_text(TEXT_AFTER_SUB,
                              reply_markup=kb(user))
    return MAIN_MENU



@run_async
@save_msg
@with_user
def create_broadcast( api: TelegramBotApi, user: TGUser, update):
    logger.info("User %s initiated broadcast.", user)
    if not user.is_admin:
        update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=kb(user))
    update.message.reply_text(TEXT_ENTER_BROADCAST)
    return BROADCAST

@run_async
@save_msg
@with_user
def send_broadcast(api: TelegramBotApi, user: TGUser, update):
    broadcast_text = update.message.text
    for u in TGUser.objects.all():
        try:
            api.bot.send_message(u.tg_id, broadcast_text)
            time.sleep(.1)
        except:
            logger.exception('Error sending broadcast to user {}'.format(u))
    update.message.reply_text(TEXT_BROADCAST_DONE, reply_markup=kb(user))

@run_async
@save_msg
@with_user
def cancel(api: TelegramBotApi, user: TGUser, update):
    logger.info("User %s canceled the conversation.", user)
    update.message.reply_text(TEXT_BYE,
                              reply_markup=ReplyKeyboardRemove())


handlers = [
    ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            MAIN_MENU: [
                rhandler(BUTTON_CHECK_REGISTRATION, check_registration_status),
                rhandler(BUTTON_AUTHORISATION, authorization),
                # rhandler(BUTTON_REGISTRATION, can_spam),
                # rhandler(BUTTON_POST_NEWS, create_broadcast)
            ],

            SCHEDULE:[
                rhandler(BUTTON_10_MAY_SCHEDULE, schedule_day),
                rhandler(BUTTON_11_MAY_SCHEDULE, schedule_day)
            ],

            CHECK_EMAIL: [MessageHandler(Filters.text, check_email),
                          CommandHandler('skip', skip_email)],

            BROADCAST: [MessageHandler(Filters.text, send_broadcast),
                        CommandHandler('skip', skip_email)]  # fixme
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
]

