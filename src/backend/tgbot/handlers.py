from functools import wraps

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import MessageHandler, Filters, run_async, ConversationHandler, CommandHandler, RegexHandler

from backend.models import Message, Invite, TGUser, Event
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.utils import logger

CHOOSING = 0
CHECK_EMAIL = 1

MENU_KEYBOARD = [[TEXT_CHECK_EMAIL, TEXT_VIEW_SCEDULE, TEXT_SUBSCRIBE]]


def save_msg(f):
    @wraps(f)
    def save(api: TelegramBotApi, update):
        Message.from_update(api, update)
        return f(api, update)

    return save


def with_user(f):
    @wraps(f)
    def get_user(api: TelegramBotApi, update):
        user = api.get_user(update.message.chat_id)
        return f(api, user, update)

    return get_user


@run_async
@save_msg
def menu(api: TelegramBotApi, update):
    user = update.message.from_user
    logger.info('User {} have started conversation.'.format(user.first_name))
    update.message.reply_text(
        TEXT_HELLO,
        reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=True))

    return CHOOSING


@run_async
@save_msg
def check_email(api: TelegramBotApi, update):
    user = update.message.from_user
    text = update.message.text
    logger.info('User {} have chosen {} '.format(user.first_name, text))
    update.message.reply_text(TEXT_ENTER_EMAIL,
                              reply_markup=ReplyKeyboardRemove())
    return CHECK_EMAIL


@run_async
@save_msg
@with_user
def email_in_list(api: TelegramBotApi, user: TGUser, update):
    email = update.message.text
    logger.info('{}'.format(email))
    if Invite.objects.filter(email=email).first() is not None:
        update.message.reply_text(TEXT_EMAIL_OK,
                                  reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=True))
    else:
        update.message.reply_text(TEXT_EMAIL_NOT_OK,
                                  reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=True))

    if user.last_checked_email != email:
        user.is_notified = False  # todo ????
        user.last_checked_email = email
        user.save()
    return CHOOSING


@run_async
@save_msg
def table_sheet(api: TelegramBotApi, update):
    schedule = '\n'.join(str(e) for e in Event.objects.all())
    update.message.reply_text('{}\n\n{}'.format(TEXT_SHOW_SCHEDULE, schedule)
                              , reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=True))
    return CHOOSING


@run_async
@save_msg
@with_user
def can_spam(api: TelegramBotApi, user: TGUser, update):
    user.is_subscribed = True
    user.save()
    logger.info('{} subscribed for notification'.format(user))
    update.message.reply_text(TEXT_AFTER_SUB,
                              reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=True))
    return CHOOSING


@run_async
@save_msg
def skip_email(api: TelegramBotApi, update):
    user = update.message.from_user
    logger.info("User %s did not send an email.", user.first_name)
    update.message.reply_text(TEXT_SKIP_EMAIL, reply_markup=ReplyKeyboardMarkup(MENU_KEYBOARD, one_time_keyboard=True))
    return CHOOSING


@run_async
@save_msg
def cancel(api: TelegramBotApi, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(TEXT_BYE,
                              reply_markup=ReplyKeyboardRemove())


handlers = [
    ConversationHandler(
        entry_points=[CommandHandler('start', menu)],

        states={
            CHOOSING: [RegexHandler('^({})$'.format(TEXT_CHECK_EMAIL), check_email),
                       RegexHandler('^({})$'.format(TEXT_VIEW_SCEDULE), table_sheet),
                       RegexHandler('^({})$'.format(TEXT_SUBSCRIBE), can_spam)],

            CHECK_EMAIL: [MessageHandler(Filters.text, email_in_list),
                          CommandHandler('skip', skip_email)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
]
