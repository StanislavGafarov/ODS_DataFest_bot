from telegram.ext import run_async, MessageHandler, Filters, CommandHandler

from backend.models import TGUser, Invite
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.tghandler import TGHandler
from backend.tgbot.utils import Decorators, logger


class CheckRegistrationStatus(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def email_in_list(self, api: TelegramBotApi, user: TGUser, update):
        email = update.message.text
        logger.info('{}'.format(email))
        if Invite.objects.filter(email__iexact=email).first() is not None:
            update.message.reply_text(TEXT_EMAIL_OK,
                                      reply_markup=self.define_keyboard(user))
        else:
            update.message.reply_text(TEXT_EMAIL_NOT_OK,
                                      reply_markup=self.define_keyboard(user))

        if user.last_checked_email != email:
            user.last_checked_email = email
            user.is_notified = True
            user.save()
        return self.MAIN_MENU

    def create_state(self):
        state = {self.CHECK_REGISTRATION_STATUS: [
            MessageHandler(Filters.text, self.email_in_list),
            CommandHandler('skip', self.skip_email)]}
        return state
