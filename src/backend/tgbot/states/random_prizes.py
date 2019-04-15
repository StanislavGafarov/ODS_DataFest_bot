import random
from telegram import ReplyKeyboardMarkup
from telegram.ext import run_async, MessageHandler, Filters
from telegram.error import Unauthorized

from backend.tgbot.tghandler import TGHandler
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.utils import Decorators, logger
from backend.models import TGUser, Prizes
from backend.tgbot.texts import *


class RandomFreePrizes(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def chosen_size(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have set his size: {} '.format(user, text))
        user.in_random_prize = True
        user.merch_size = text
        user.save()
        update.message.reply_text(TEXT_CHOSEN_SIZE.format(text), reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def change_size(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have decided to change his size'.format(user, text))
        update.message.reply_text(TEXT_CHANGE_SIZE, reply_markup=ReplyKeyboardMarkup(self.SIZE_KEYBOARD,
                                                                                     one_time_keyboard=True,
                                                                                     resize_keyboard=True))
        return self.CHOOSEN_SIZE

    # ADMIN
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def admin_start_drowing(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('ADMIN {} have chosen {}'.format(user, text))
        prizes = Prizes.objects.values()
        if prizes.count() == 0:
            update.message.reply_text(TEXT_EMPTY_TABLE_PRIZE, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU
        else:
            for row in prizes:
                merch_size = row.get('merch_size')
                sample_size = row.get('quantity')
                all_users = TGUser.objects.filter(in_random_prize=True, merch_size=merch_size)\
                    .exclude(win_random_prize=True).values_list('tg_id', flat=True)
                winners = random.sample(list(all_users), sample_size)
                for winner in winners:
                    win_user = TGUser.objects.get(tg_id=winner).first()
                    win_user.win_random_prize = True
                    win_user.save()
                    logger.info('User {} email:{} win the prize in category {}'
                                .format(win_user.name, win_user.last_checked_email, merch_size))
                    try:
                        api.bot.send_message(win_user.tg_id, TEXT_CONGRATULATION)
                    except Unauthorized:
                        logger.info('{} blocked'.format(user))

        update.message.reply_text('Done', reply_markup=self.define_keyboard(user))
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
            self.rhandler(BUTTON_FULL_BACK, self.full_back),
            MessageHandler(Filters.text, self.unknown_command)
        ],
            self.CHANGE_SIZE: [
                self.rhandler(BUTTON_CHANGE_SIZE, self.change_size),
                self.rhandler(BUTTON_FULL_BACK, self.full_back),
                MessageHandler(Filters.text, self.unknown_command)
        ],
            self.DRAW_PRIZES: [
                self.rhandler(BUTTON_START_DRAWING, self.admin_start_drowing),
                self.rhandler(BUTTON_FULL_BACK, self.full_back),
                MessageHandler(Filters.text, self.unknown_command)
            ]
        }
        return state