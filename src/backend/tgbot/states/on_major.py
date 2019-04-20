from telegram.ext import run_async, MessageHandler, Filters

from backend.models import TGUser
from backend.tgbot.texts import *
from backend.tgbot.tghandler import TGHandler
from backend.tgbot.utils import Decorators, logger
from backend.tgbot.states.secret_code import SECRET_CODE

class OnMajor(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def major_check_code(self, api, user: TGUser, update):
        code = update.message.text
        logger.info('User {} sent {} code'.format(user, code))
        if code == SECRET_CODE:
            user.on_major = True
            user.save()
            update.message.reply_text(TEXT_MAJOR_CODE_OK,
                                      reply_markup=self.define_keyboard(user))
        else:
            update.message.reply_text(TEXT_MAJOR_CODE_NOT_OK,
                                      reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    def create_state(self):
        state = {self.MAJOR_CHECK_CODE: [
            MessageHandler(Filters.text, self.major_check_code)
            ]}
        return state
