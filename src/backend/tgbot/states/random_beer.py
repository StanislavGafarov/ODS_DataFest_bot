import random

from telegram import ReplyKeyboardRemove
from telegram.ext import run_async, MessageHandler, Filters, CommandHandler

from backend.tgbot.tghandler import TGHandler
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.utils import Decorators, logger
from backend.models import TGUser, RandomBeerUser
from telegram.error import Unauthorized


class RandomBeer(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def accepted_rules(self, api: TelegramBotApi, user: TGUser, update,  random_beer_user: RandomBeerUser):
        text = update.message.text
        logger.info(' {} '.format(text))
        user.in_random_beer = True
        user.save()
        logger.info('User {} have accepted random beer rules'.format(user))
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
    def rb_unknown_command(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        text = update.message.text
        logger.info('User {} wrote unknown command: {}'.format(user, text))
        update.message.reply_text(TEXT_UNKNOWN_COMMAND, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def get_tg_nick(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        prev_field_val = random_beer_user.tg_nickname
        tg_nick = update.message.text
        random_beer_user.tg_nickname = tg_nick
        random_beer_user.save()
        logger.info('User {} fill tg_nickname with {} '.format(user, tg_nick))
        if prev_field_val is not None:
            update.message.reply_text(TEXT_SUCCESSFULLY_CHANGED +'\n'+ TEXT_RANDOM_BEER_MENU
                                      .format(random_beer_user.tg_nickname, random_beer_user.ods_nickname,
                                              random_beer_user.social_network_link)
                                      , reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU
        update.message.reply_text(TEXT_NEED_ODS_NICK, reply_markup=ReplyKeyboardRemove())
        return self.RANDOM_BEER_ODS_NICK

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def skip_tg_nick(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        prev_field_val = random_beer_user.tg_nickname
        logger.info('User {} decided to skip tg_nickname filling'.format(user))
        if prev_field_val is not None:
            update.message.reply_text(TEXT_SUCCESSFULLY_CHANGED +'\n'+ TEXT_RANDOM_BEER_MENU
                                      .format(random_beer_user.tg_nickname, random_beer_user.ods_nickname,
                                              random_beer_user.social_network_link)
                                      , reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU
        random_beer_user.tg_nickname = '-'
        random_beer_user.save()
        update.message.reply_text(TEXT_NEED_ODS_NICK, reply_markup=ReplyKeyboardRemove())
        return self.RANDOM_BEER_ODS_NICK

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def get_ods_nick(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        prev_field_val = random_beer_user.ods_nickname
        ods_nick = update.message.text
        random_beer_user.ods_nickname = ods_nick
        random_beer_user.save()
        logger.info('User {} fill ods_nickname with {} '.format(user, ods_nick))
        if prev_field_val is not None:
            update.message.reply_text(TEXT_SUCCESSFULLY_CHANGED +'\n'+ TEXT_RANDOM_BEER_MENU
                                      .format(random_beer_user.tg_nickname, random_beer_user.ods_nickname,
                                              random_beer_user.social_network_link)
                                      , reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU

        update.message.reply_text(TEXT_NEED_SN_LINK, reply_markup=ReplyKeyboardRemove())
        return self.RANDOM_BEER_SN_LINK

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def skip_ods_nick(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        prev_field_val = random_beer_user.ods_nickname
        logger.info('User {} decided to skip ods_nickname filling'.format(user))
        if prev_field_val is not None:
            update.message.reply_text(TEXT_SUCCESSFULLY_CHANGED +'\n'+ TEXT_RANDOM_BEER_MENU
                                      .format(random_beer_user.tg_nickname, random_beer_user.ods_nickname,
                                              random_beer_user.social_network_link)
                                      , reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU
        random_beer_user.ods_nickname = '-'
        random_beer_user.save()
        update.message.reply_text(TEXT_NEED_SN_LINK, reply_markup=ReplyKeyboardRemove())
        return self.RANDOM_BEER_SN_LINK

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def get_sn_link(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        prev_field_val = random_beer_user.social_network_link
        sn_link = update.message.text
        random_beer_user.social_network_link = sn_link
        random_beer_user.save()
        logger.info('User {} fill social_network_link '.format(user))
        if prev_field_val is not None:
            update.message.reply_text(TEXT_SUCCESSFULLY_CHANGED +'\n'+ TEXT_RANDOM_BEER_MENU
                                      .format(random_beer_user.tg_nickname, random_beer_user.ods_nickname,
                                              random_beer_user.social_network_link)
                                      , reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU
        update.message.reply_text(TEXT_RANDOM_BEER_MENU.format(random_beer_user.tg_nickname,
                                                               random_beer_user.ods_nickname,
                                                               random_beer_user.social_network_link)
                                  , reply_markup=self.random_beer_keyboard(random_beer_user))
        return self.RANDOM_BEER_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def skip_sn_link(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        prev_field_val = random_beer_user.social_network_link
        logger.info('User {} decided to skip social_network_link filling'.format(user))
        if prev_field_val is not None:
            update.message.reply_text(TEXT_SUCCESSFULLY_CHANGED +'\n'+ TEXT_RANDOM_BEER_MENU
                                      .format(random_beer_user.tg_nickname, random_beer_user.ods_nickname,
                                              random_beer_user.social_network_link)
                                      , reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU
        random_beer_user.social_network_link = '-'
        random_beer_user.save()
        update.message.reply_text(TEXT_RANDOM_BEER_MENU.format(random_beer_user.tg_nickname,
                                                               random_beer_user.ods_nickname,
                                                               random_beer_user.social_network_link)
                                  , reply_markup=self.random_beer_keyboard(random_beer_user))
        return self.RANDOM_BEER_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def change_field(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        text = update.message.text
        mapper = {BUTTON_CHANGE_TG_NICK: self.RANDOM_BEER_TG_NICK,
                  BUTTON_CHANGE_ODS_NICK: self.RANDOM_BEER_ODS_NICK,
                  BUTTON_CHANGE_SN_LINK: self.RANDOM_BEER_SN_LINK}
        logger.info('User {} have decided to {}'.format(user, text))
        update.message.reply_text(TEXT_CHANGE_FIELD.format(text.lower()), reply_markup=ReplyKeyboardRemove())
        return mapper[text]

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def find_match(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        # TODO: Refactor monkey code here
        text = update.message.text
        logger.info('User {} have choosen {}'.format(user, text))
        if self.check_info(random_beer_user):
            logger.info('User {} do not have enought info for participating'.format(user))
            update.message.reply_text(TEXT_NOT_ENOUGH_INFO, reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU

        if random_beer_user.is_busy:
            logger.info('User {} is busy'.format(user))
            update.message.reply_text(TEXT_SHOULD_END_MEETING, reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU

        if not self.will_have_pair(random_beer_user):
            logger.info('User {} will not have pair and should wait'.format(user))
            update.message.reply_text(TEXT_NOT_ENOUGH_PARTICIPANTS,
                                      reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU

        else:
            if random_beer_user.random_beer_try == 10:
                update.message.reply_text(TEXT_LIMIT_IS_OVER+ '\n'+ TEXT_GOTO_RANDOM_COFFEE
                                          , reply_markup=self.random_beer_keyboard(random_beer_user))
                return self.RANDOM_BEER_MENU

            else:

                pair_id = self.get_match(random_beer_user)
                pair_user = RandomBeerUser.objects.filter(tg_user_id=pair_id).first()
                pair_user.is_busy = True
                random_beer_user.is_busy = True
                random_beer_user.prev_pair = pair_id
                pair_user.prev_pair = random_beer_user.tg_user_id
                random_beer_user.random_beer_try += 1
                pair_user.random_beer_try += 1
                pair_user.save()
                random_beer_user.save()
                self.send_notification(pair_user, random_beer_user, api)
                logger.info('User {} will meet with user {}'.format(random_beer_user.email, pair_user.email))
                update.message.reply_text(TEXT_RANDOM_BEER_MATCH
                                          .format(pair_user.tg_nickname, pair_user.ods_nickname,
                                                  pair_user.social_network_link),
                                          reply_markup=self.random_beer_keyboard(random_beer_user))
                return self.RANDOM_BEER_MENU

    def get_match(self, random_beer_user: RandomBeerUser):
        posible_pair_list = RandomBeerUser.objects.filter(accept_rules=True)\
                .exclude(is_busy=True).exclude(random_beer_try=10).exclude(tg_user_id=random_beer_user.tg_user_id)\
                .exclude(tg_nickname='-', ods_nickname='-', social_network_link='-') \
                .exclude(tg_nickname=None, ods_nickname=None, social_network_link=None) \
                .exclude(tg_user_id=random_beer_user.prev_pair).values_list('tg_user_id', flat=True)
        return random.choice(posible_pair_list)

    def send_notification(self, user, data, api):
        try:
            api.bot.send_message(user.tg_user_id, TEXT_RANDOM_BEER_MATCH
                                 .format(data.tg_nickname, data.ods_nickname, data.social_network_link))
        except Unauthorized:
            api.bot.send_message(data.tg_user_id, TEXT_FAILED_SENT)
            logger.info('{} blocked bots notifications'.format(user.email))

    def will_have_pair(self, random_beer_user):
        random_beer_table = RandomBeerUser.objects.filter(accept_rules=True) \
            .exclude(is_busy=True).exclude(random_beer_try=10).exclude(tg_user_id=random_beer_user.tg_user_id) \
            .exclude(tg_nickname='-', ods_nickname='-', social_network_link='-') \
            .exclude(tg_nickname=None, ods_nickname=None, social_network_link=None) \
            .exclude(tg_user_id=random_beer_user.prev_pair).values()
        return random_beer_table.count() > 0

    def check_info(self, rb_user):
        return rb_user.tg_nickname == '-' and rb_user.ods_nickname == '-' and rb_user.social_network_link == '-'

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def end_meeting(self, api: TelegramBotApi, user: TGUser, update, random_beer_user: RandomBeerUser):
        logger.info('{} have finished the meeting'.format(random_beer_user.email))
        random_beer_user.is_busy = False
        # pair_user = RandomBeerUser.objects.filter(tg_user_id=random_beer_user.prev_pair).first()
        # pair_user.is_busy = False
        random_beer_user.save()
        # pair_user.save()
        update.message.reply_text(TEXT_END_MEETING, reply_markup=self.random_beer_keyboard(random_beer_user))
        return self.RANDOM_BEER_MENU

    def create_state(self):
        state = {
            self.RANDOM_BEER_RULES: [
                self.rhandler(BUTTON_ACCEPT_RULES, self.accepted_rules),
                self.rhandler(BUTTON_DECLINE_RULES, self.decline_rules),
                MessageHandler(Filters.text, self.rb_unknown_command)
            ],
            self.RANDOM_BEER_TG_NICK: [
                MessageHandler(Filters.text, self.get_tg_nick),
                CommandHandler('skip', self.skip_tg_nick)
            ],
            self.RANDOM_BEER_ODS_NICK: [
                MessageHandler(Filters.text, self.get_ods_nick),
                CommandHandler('skip', self.skip_ods_nick)
            ],
            self.RANDOM_BEER_SN_LINK: [
                MessageHandler(Filters.text, self.get_sn_link),
                CommandHandler('skip', self.skip_sn_link)
            ],
            self.RANDOM_BEER_MENU: [
                self.rhandler(BUTTON_CHANGE_SN_LINK, self.change_field),
                self.rhandler(BUTTON_CHANGE_ODS_NICK, self.change_field),
                self.rhandler(BUTTON_CHANGE_TG_NICK, self.change_field),
                self.rhandler(BUTTON_FIND_MATCH, self.find_match),
                self.rhandler(BUTTON_END_MEETING, self.end_meeting),
                self.rhandler(BUTTON_FULL_BACK, self.full_back),
                MessageHandler(Filters.text, self.rb_unknown_command)
            ]
        }
        return state
