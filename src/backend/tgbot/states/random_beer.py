from telegram import ReplyKeyboardRemove
from telegram.ext import run_async, MessageHandler, Filters, CommandHandler

from backend.tgbot.tghandler import TGHandler
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.utils import Decorators, logger
from backend.models import TGUser, RandomBeerUser

#TODO: Change all this fields
class RandomBeer(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def accepted_rules(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        text = update.message.text
        user.in_random_beer = True
        user.save()
        random_beer_user.accept_rules = True
        random_beer_user.save()
        update.message.reply_text(TEXT_RULES_ACCEPTED_NEED_TG_NICK, reply_markup=ReplyKeyboardRemove())
        return self.RANDOM_BEER_TG_NICK

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def decline_rules(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        text = update.message.text
        logger.info('User {} have declined random beer rules'.format(user))
        update.message.reply_text(TEXT_RULES_NOT_ACCEPTED, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def get_tg_nick(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        tg_nick = update.message.text
        random_beer_user.tg_nickname = tg_nick
        random_beer_user.save()
        logger.info('User {} fill tg_nickname with {} '.format(user, tg_nick))
        update.message.reply_text(TEXT_NEED_ODS_NICK, reply_markup=ReplyKeyboardRemove())
        return self.RANDOM_BEER_ODS_NICK

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def skip_tg_nick(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        logger.info('User {} decided to skip tg_nickname filling')
        update.message.reply_text(TEXT_NEED_ODS_NICK, reply_markup=ReplyKeyboardRemove())
        return self.RANDOM_BEER_ODS_NICK

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def get_ods_nick(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        ods_nick = update.message.text
        random_beer_user.ods_nickname = ods_nick
        random_beer_user.save()
        logger.info('User {} fill ods_nickname with {} '.format(user, ods_nick))
        update.message.reply_text(TEXT_NEED_SN_LINK, reply_markup=ReplyKeyboardRemove())
        return self.RANDOM_BEER_SN_LINK

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def skip_ods_nick(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        logger.info('User {} decided to skip ods_nickname filling')
        update.message.reply_text(TEXT_NEED_SN_LINK, reply_markup=ReplyKeyboardRemove())
        return self.RANDOM_BEER_SN_LINK

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def get_sn_link(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        sn_link = update.message.text
        random_beer_user.social_network_link = sn_link
        random_beer_user.save()
        logger.info('User {} fill social_network_link '.format(user, sn_link))
        update.message.reply_text(TEXT_RANDOM_BEER_MENU, reply_markup=self.random_beer_keyboard(random_beer_user))
        return self.RANDOM_BEER_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def skip_sn_link(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        logger.info('User {} decided to skip social_network_link filling')
        update.message.reply_text(TEXT_RANDOM_BEER_MENU, reply_markup=self.random_beer_keyboard(random_beer_user))
        return self.RANDOM_BEER_MENU


    def create_state(self):
        state = {
            self.RANDOM_BEER_RULES: [
                self.rhandler(BUTTON_ACCEPT_RULES, self.accepted_rules),
                self.rhandler(BUTTON_DECLINE_RULES, self.decline_rules),
                MessageHandler(Filters.text, self.unknown_command)
            ],
            self.RANDOM_BEER_TG_NICK: [
                MessageHandler(Filters.text, self.get_tg_nick),
                CommandHandler('skip', self.skip_tg_nick)
            ],
            self.RANDOM_BEER_ODS_NICK:[
                MessageHandler(Filters.text, self.get_ods_nick),
                CommandHandler('skip', self.skip_ods_nick)
            ],
            self.RANDOM_BEER_SN_LINK: [
                MessageHandler(Filters.text, self.get_sn_link),
                CommandHandler('skip', self.skip_sn_link)
            ],
            self.RANDOM_BEER_MENU: [
                self.rhandler(BUTTON_FULL_BACK, self.full_back),
                MessageHandler(Filters.text, self.unknown_command)
            ]
        }
        return state
