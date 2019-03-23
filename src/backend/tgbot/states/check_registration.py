from telegram.ext import run_async
from backend.tgbot.utils import logger, save_msg, with_user
from backend.tgbot.base import TelegramBotApi
from backend.models import Invite, TGUser
from backend.tgbot.texts import *
from backend.tgbot.states.main_menu import MAIN_MENU, make_keyboard


@run_async
@save_msg
@with_user
def email_in_list(api: TelegramBotApi, user: TGUser, update):
    email = update.message.text
    logger.info('{}'.format(email))
    if Invite.objects.filter(email=email).first() is not None:
        update.message.reply_text(TEXT_EMAIL_OK,
                                  reply_markup=make_keyboard(user))
    else:
        update.message.reply_text(TEXT_EMAIL_NOT_OK,
                                  reply_markup=make_keyboard(user))

    if user.last_checked_email != email:
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


# TODO: add to handlers {CHECK_REGISTRATION_STATUS: [MessageHandler(Filters.text, email_in_list), CommandHandler('skip', skip_email)]}