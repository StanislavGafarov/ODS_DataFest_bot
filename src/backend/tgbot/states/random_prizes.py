from telegram import ReplyKeyboardMarkup
from telegram.ext import run_async

from backend.tgbot.tghandler import TGHandler
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.utils import Decorators, logger
from backend.models import TGUser
from backend.tgbot.texts import *


class RandomFreePrizes(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def chosen_size(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have set his size: {} '.format(user, text))
        user.in_random_prize = True
        user.merch_size = text
        user.save()
        update.message.reply_text(TEXT_CHOOSEN_SIZE.format(text), reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def change_size(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have decided to change his size'.format(user, text))
        update.message.reply_text(TEXT_СHANGE_SIZE, reply_markup=ReplyKeyboardMarkup(self.SIZE_KEYBOARD,
                                                                                     one_time_keyboard=True,
                                                                                     resize_keyboard=True))
        return self.CHOOSEN_SIZE

    # ADMIN
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def admin_chosen_category(self, api: TelegramBotApi, user: TGUser, update):
        return self.MAIN_MENU

    def create_state(self):
        state = {self.CHOOSEN_SIZE: [
            self.rhandler(BUTTON_XS_SIZE, self.chosen_size),
            self.rhandler(BUTTON_S_SIZE, self.chosen_size),
            self.rhandler(BUTTON_M_SIZE, self.chosen_size),
            self.rhandler(BUTTON_L_SIZE, self.chosen_size),
            self.rhandler(BUTTON_XL_SIZE, self.chosen_size),
            self.rhandler(BUTTON_XXL_SIZE, self.chosen_size),
            self.rhandler(BUTTON_XXXL_SIZE, self.chosen_size),
            self.rhandler(BUTTON_FULL_BACK, self.full_back)
        ],
            self.CHANGE_SIZE: [
                self.rhandler(BUTTON_CHANGE_SIZE, self.change_size),
                self.rhandler(BUTTON_FULL_BACK, self.full_back)
        ],
            self.START_RANDOM_PRIZE:[
                self.rhandler(BUTTON_FULL_BACK, self.full_back)
            ]
        }
        return state