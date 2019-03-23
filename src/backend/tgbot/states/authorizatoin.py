from telegram.ext import run_async
from backend.tgbot.utils import logger, save_msg, with_user
from backend.tgbot.base import TelegramBotApi
from backend.models import Invite, TGUser
from backend.tgbot.texts import *
from backend.tgbot.states.main_menu import MAIN_MENU, make_keyboard
from telegram import ReplyKeyboardRemove

CHECK_CODE = 99
@run_async
@save_msg
@with_user
def auth_check_email(api: TelegramBotApi, user: TGUser, update):
    email = update.message.text
    logger.info('{}'.format(email))
    if Invite.objects.filter(email=email).first() is not None:
        update.message.reply_text(TEXT_AUTH_EMAIL_OK, reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(TEXT_EMAIL_NOT_OK,
                                  reply_markup=make_keyboard(user))
        return MAIN_MENU

    if user.last_checked_email != email:
        user.last_checked_email = email
        user.save()
    return CHECK_CODE

@run_async
@save_msg
@with_user
def auth_check_code(api: TelegramBotApi, user: TGUser, update):
    code = update.message.text
    if Invite.objects.filter(email=user.last_checked_email, code=code):
        user.is_authorized = True
        update.message.reply_text(TEXT_CODE_OK,
                                  reply_markup=make_keyboard(user))
    else:
        update.message.reply_text(TEXT_CODE_NOT_OK,
                                  reply_markup=make_keyboard(user))
    return MAIN_MENU


# TODO: add to handlers
''' {AUTHORIZATION: [MessageHandler(Filters.text, auth_check_email),
    CHECK_CODE: [MessageHandler(Filters.text, auth_check_code)]
} '''