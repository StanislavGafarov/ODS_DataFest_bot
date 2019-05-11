import random
import time
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
        def calculate_winners(prizes):
            for prize in prizes:
                merch_size = prize.merch_size
                sample_size = prize.quantity
                if not prize.quantity:
                    continue
                all_users = TGUser.objects.filter(in_random_prize=True, merch_size=merch_size) \
                    .exclude(win_random_prize=True).values_list('tg_id', flat=True)

                winners = random.sample(list(all_users),
                                        sample_size if len(list(all_users)) > sample_size else len(list(all_users))
                                        )
                # обновить только 1 поле.
                TGUser.objects.filter(tg_id__in=winners).update(win_random_prize=True)

        def broadcast_users(users, text):
            counter = 0
            error_counter = 0
            for user in users:
                counter += 1
                try:
                    api.bot.send_message(user.tg_id, text)
                    time.sleep(.1)
                    continue
                except Unauthorized:
                    logger.info('{} blocked'.format(user))
                    user.delete()
                except:
                    logger.exception('Error sending broadcast to user {}'.format(user))
                error_counter += 1
            return counter, error_counter

        def broadcast_winners(api, admin_user):
            def get_winner_list(users):
                for prize in Prizes.objects.all():
                    user_list = "\n".join([f"{win_user.name}, {win_user.last_checked_email}"
                     for win_user in users.filter(merch_size=prize.merch_size)])
                    if user_list:
                        yield f"{prize.merch_size}:\n{user_list}"

            users = TGUser.objects.filter(in_random_prize=True, win_random_prize=True)
            for msg in get_winner_list(users):
                api.bot.send_message(admin_user.tg_id, msg)
            total, fail = broadcast_users(users, TEXT_CONGRATULATION)
            api.bot.send_message(admin_user.tg_id, TEXT_RANDOM_PRIZE_BROADCAST_DONE.format(total, fail))

        def broadcast_loosers(api, admin_user):
            users = TGUser.objects.filter(in_random_prize=True, win_random_prize=False)
            total, fail = broadcast_users(users, TEXT_RANDOM_PRIZE_NOT_SUCCEED)
            api.bot.send_message(admin_user.tg_id, TEXT_RANDOM_PRIZE_NOT_SUCCEED_BROADCAST_DONE.format(total, fail))

        def broadcast_participants(api, admin_user):
            broadcast_winners(api, admin_user)
            time.sleep(0.5)
            broadcast_loosers(api, admin_user)

        text = update.message.text
        logger.info('ADMIN {} have chosen {}'.format(user, text))

        if not Prizes.objects.count():
            update.message.reply_text(TEXT_EMPTY_TABLE_PRIZE, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU

        calculate_winners(Prizes.objects.all())
        update.message.reply_text(TEXT_RANDOM_PRIZE_BROADCAST_STARTED, reply_markup=self.define_keyboard(user))
        TGHandler.add_task(broadcast_participants, api, user)
        return self.MAIN_MENU

    def create_state(self):
        state = {self.CHOOSEN_SIZE: [
            self.rhandler(BUTTON_XS_SIZE, self.chosen_size),
            self.rhandler(BUTTON_S_SIZE, self.chosen_size),
            self.rhandler(BUTTON_M_SIZE, self.chosen_size),
            self.rhandler(BUTTON_L_SIZE, self.chosen_size),
            self.rhandler(BUTTON_XL_SIZE, self.chosen_size),
            self.rhandler(BUTTON_XXL_SIZE, self.chosen_size),
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