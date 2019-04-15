from telegram import ReplyKeyboardRemove
from telegram.ext import run_async, MessageHandler, Filters, CommandHandler

from backend.models import TGUser, Invite
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.tghandler import TGHandler
from backend.tgbot.utils import Decorators, logger


class Authorization(TGHandler):
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
        invite = Invite.objects.filter(email=user.last_checked_email, code=code).first()
        if code is not None and invite is not None:
            if hasattr(invite, 'tguser'):
                logger.info('{} tried to sign as {}'.format(user, invite.tguser))
                update.message.reply_text(TEXT_EMAIL_USED_BY_OTHER_USER, reply_markup=self.define_keyboard(user))
            else:
                user.invite = invite
                user.is_authorized = True
                logger.info('{} is authorized'.format(user))
                user.save()
                update.message.reply_text(TEXT_CODE_OK,
                                          reply_markup=self.define_keyboard(user))
        else:
            logger.info('{} is NOT authorized'.format(user))
            update.message.reply_text(TEXT_CODE_NOT_OK,
                                      reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    def create_state(self):
        state = {self.AUTHORIZATION: [MessageHandler(Filters.text, self.auth_check_email),
                                      CommandHandler('skip', self.skip_email)],
                 self.CHECK_CODE: [MessageHandler(Filters.text, self.auth_check_code)]}
        return state
