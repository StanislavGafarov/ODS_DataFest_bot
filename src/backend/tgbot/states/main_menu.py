import traceback

from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup, Location
from telegram.error import Unauthorized
from telegram.ext import run_async, MessageHandler, Filters
from django.db.models import Count

from backend.google_spreadsheet_client import GoogleSpreadsheet
from backend.models import TGUser, Invite, Prizes, RandomBeerUser, News
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.tghandler import TGHandler
from backend.tgbot.utils import logger, Decorators
from backend.tgbot.states.nvidia_answers import *


class FLACON:
    location = Location(latitude=55.805120, longitude=37.584590)
    map = 'https://datafest.ru/static/img/design/nav-c.jpg'


class MainMenu(TGHandler):
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def check_registration_status(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_ENTER_EMAIL, reply_markup=ReplyKeyboardRemove())
        return self.CHECK_REGISTRATION_STATUS

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def authorization(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_ENTER_EMAIL, reply_markup=ReplyKeyboardRemove())
        return self.AUTHORIZATION

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def get_news(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        if user.has_news_subscription:
            custom_keyboard = [[BUTTON_NEWS_UNSUBSCRIPTION,
                                BUTTON_FULL_BACK,
                                BUTTON_GET_LAST_5_NEWS
                                ]]
        else:
            custom_keyboard = [[BUTTON_NEWS_SUBSCRIPTION,
                                BUTTON_FULL_BACK,
                                BUTTON_GET_LAST_5_NEWS
                                ]]
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NEWS, reply_markup=ReplyKeyboardMarkup(custom_keyboard
                                                                              , one_time_keyboard=True
                                                                              , resize_keyboard=True))
        return self.GET_NEWS

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def not_ready_yet(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def ready_but_muted(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_WILL_BE_ON_DATAFEST, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def get_schedule(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        update.message.reply_text(TEXT_SHOW_SCHEDULE, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def show_path(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        api.bot.send_location(user.tg_id, location=FLACON.location)
        api.bot.send_photo(user.tg_id, photo=FLACON.map,
                           caption=f"{TEXT_SHOW_PATH_MAP_CAPTION}. {TEXT_SHOW_PATH_MORE_INFO}",
                           reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def want_jetson(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        user.in_nvidia_jetsone = True
        user.save()
        update.message.reply_text(TEXT_JETSON, reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU
    # AUTHORIZED
    # @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    # def on_major(self, api: TelegramBotApi, user: TGUser, update):
    #     text = update.message.text
    #     logger.info('User {} have chosen {} '.format(user, text))
    #     if not user.is_authorized:
    #         update.message.reply_text(TEXT_NOT_AUTHORIZED, reply_markup=self.define_keyboard(user))
    #         return self.MAIN_MENU
    #     else:
    #         if user.on_major:
    #             update.message.reply_text(TEXT_ALREADY_ON_MAJOR, reply_markup=self.define_keyboard(user))
    #             return self.MAIN_MENU
    #         else:
    #             update.message.reply_text(TEXT_MAJOR_CODE, reply_markup=ReplyKeyboardRemove())
    #             return self.ON_MAJOR

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def participate_random_prize(self, api: TelegramBotApi, user: TGUser, update):
        text = update.message.text
        logger.info('User {} have chosen {} '.format(user, text))
        if not user.is_authorized:
            update.message.reply_text(TEXT_NOT_AUTHORIZED, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU
        # ON Major
        # if not user.on_major:
        #     update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        #     return self.MAIN_MENU
        if user.merch_size is None:
            update.message.reply_text(TEXT_CHOOSE_YOUR_SIZE, reply_markup=ReplyKeyboardMarkup(self.SIZE_KEYBOARD,
                                                                                              one_time_keyboard=True,
                                                                                              resize_keyboard=True))
            return self.CHOOSEN_SIZE
        else:
            custom_keyboard = [[BUTTON_CHANGE_SIZE, BUTTON_FULL_BACK]]
            update.message.reply_text(TEXT_KNOW_SIZE.format(user.merch_size)
                                      , reply_markup=ReplyKeyboardMarkup(custom_keyboard, one_time_keyboard=True,
                                                                         resize_keyboard=True))
            return self.CHANGE_SIZE

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_random_beer_user)
    def participate_random_beer(self, api: TelegramBotApi,  user: TGUser, update, random_beer_user: RandomBeerUser):
        text = update.message.text
        logger.info('User {} have choosen {}'.format(user, text))
        # ON Major
        # if not user.on_major:
        #     update.message.reply_text(TEXT_NOT_READY_YET, reply_markup=self.define_keyboard(user))
        #     return self.MAIN_MENU
        if not user.is_authorized:
            update.message.reply_text(TEXT_NOT_AUTHORIZED, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU
        if random_beer_user.accept_rules:
            update.message.reply_text(TEXT_RANDOM_BEER_MENU
                                      .format(random_beer_user.tg_nickname, random_beer_user.ods_nickname,
                                              random_beer_user.social_network_link),
                                      reply_markup=self.random_beer_keyboard(random_beer_user))
            return self.RANDOM_BEER_MENU
        else:
            custom_keyboard = [[BUTTON_ACCEPT_RULES, BUTTON_DECLINE_RULES]]
            update.message.reply_text(TEXT_RULES, reply_markup=ReplyKeyboardMarkup(custom_keyboard
                                                                                   , one_time_keyboard=True
                                                                                   , resize_keyboard=True))
            return self.RANDOM_BEER_RULES

    # ADMIN
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def create_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU
        text = update.message.text
        logger.info('ADMIN {} have choosen {}'.format(user, text))
        user_count = TGUser.objects.count()
        subscription_count = TGUser.objects.filter(has_news_subscription=True).count()
        winner_count = TGUser.objects.filter(win_random_prize=True).count()
        admin_count = TGUser.objects.filter(is_admin=True).count()

        statistics_text = TEXT_NEWS_STAT.format(user_count, subscription_count, winner_count, admin_count)
        msg = f"{statistics_text}\n{TEXT_BROADCAST_CHOOSE_GROUP}"
        update.message.reply_text(msg,  reply_markup=self.broadcast_group_keyboard(user))
        return self.BROADCAST

    # REFRESH INVITES
    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def refresh_invites_and_notify(self, api: TelegramBotApi, user: TGUser, update):
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU
        gss_client = GoogleSpreadsheet(client_secret_path='./backend/tgbot/client_secret.json')
        logger.info("ADMIN %s initiated invites refresh.", user)
        update.message.reply_text(TEXT_START_INVITE_REFRESH)
        try:
            new_invites_count = gss_client.update_invites()
            update.message.reply_text(TEXT_REPORT_INVITE_COUNT.format(new_invites_count))
            notification_count = send_notifications(api)
            update.message.reply_text(TEXT_REPORT_NOTIFICATION_COUNT.format(notification_count),
                                      reply_markup=self.define_keyboard(user))
        except:
            update.message.reply_text(TEXT_REPORT_INVITE_REFRESH_ERROR + '\n' + traceback.format_exc(),
                                      reply_markup=self.define_keyboard(user))
            logger.exception('error updating invites')
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def draw_prizes(self, api: TelegramBotApi, user: TGUser, update):
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU
        text = update.message.text
        logger.info('ADMIN {} have choosen {}'.format(user, text))
        group_by_merch = TGUser.objects.values('merch_size').annotate(dcount=Count('merch_size'))
        users_merch_table = ''
        for row in group_by_merch:
            users_merch_table += '\n' + str(row.get('merch_size')) + ' : ' + str(row.get('dcount'))

        prizes_info = Prizes.objects.values()
        prizes_table = ''
        for row in prizes_info:
            prizes_table += '\n' + str(row.get('merch_size')) + ' : ' + str(row.get('quantity'))

        update.message.reply_text(TEXT_START_RANDOM_PRIZE.format(users_merch_table, prizes_table)
                                  , reply_markup=ReplyKeyboardMarkup([[BUTTON_START_DRAWING, BUTTON_FULL_BACK]]
                                                                     , one_time_keyboard=True,
                                                                     resize_keyboard=True))
        return self.DRAW_PRIZES

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def draw_jetson(self, api: TelegramBotApi, user: TGUser, update):
        if not user.is_admin:
            update.message.reply_text(TEXT_NOT_ADMIN, reply_markup=self.define_keyboard(user))
            return self.MAIN_MENU
        text = update.message.text
        logger.info('ADMIN {} have choosen {}'.format(user, text))
        gss_client = GoogleSpreadsheet(client_secret_path='./backend/tgbot/client_secret.json')
        df = gss_client.get_data('NVIDIA_JETSONE')
        df = df.rename(columns=NVIDIA_MAPPER)
        winners = df[(df.rnn_question == RNN_ANSWER)&(df.low_level_library_question == LOW_LEVEL_LIBRARY_ANSWER)&
                     (df.decrease_dimension_question == DECREASE_DIMENSION_ANSWER) & (df.name != 'Тест')]
        update.message.reply_text('Количество пользователей давших правильный ответ: {}'.format(winners.shape[0]))
        if winners.shape[0] > 3:
            winners = winners.sample(3)

        who_win = 'Победители: '
        for row in winners[['name', 'surname', 'email', 'tel']].itertuples():
            who_win = who_win + '\n Имя: {}, Фамилия: {}, email: {}, tel: {}'.format(row[1], row[2], row[3],
                                                                                     row[4])
        update.message.reply_text(who_win)

        fail_count = 0
        fail_list = []
        for winner in winners.email.tolist():
            try:
                nvidia_winner = TGUser.objects.filter(last_checked_email__iexact=winner).first()
                api.bot.send_message(nvidia_winner.tg_id, TEXT_JETSON_WIN)
                logger.info('email {} has received notification'.format(winner))
            except:
                logger.info('email {} has NOT received notification'.format(winner))
                fail_count += 1
                fail_list.append(winner)
        if fail_count != 0:
            update.message.reply_text('C ' + ' '.join(fail_list) + 'мы не смогли связаться',
                                      reply_markup=self.define_keyboard(user))
        update.message.reply_text('Выполнено.',
                                  reply_markup=self.define_keyboard(user))
        #TODO sent notification for loosers
        return self.MAIN_MENU

    def create_state(self):
        state = {self.MAIN_MENU: [
            self.rhandler(BUTTON_CHECK_REGISTRATION, self.check_registration_status),
            self.rhandler(BUTTON_AUTHORISATION, self.authorization),
            self.rhandler(BUTTON_NEWS, self.get_news),
            self.rhandler(BUTTON_SCHEDULE, self.get_schedule),
            self.rhandler(BUTTON_SHOW_PATH, self.show_path),

            # self.rhandler(BUTTON_PARTICIPATE_IN_RANDOM_PRIZE, self.ready_but_muted),
            self.rhandler(BUTTON_PARTICIPATE_IN_RANDOM_PRIZE, self.participate_random_prize),
            # self.rhandler(BUTTON_RANDOM_BEER, self.ready_but_muted),
            self.rhandler(BUTTON_RANDOM_BEER, self.participate_random_beer),

            self.rhandler(BUTTON_JETSON, self.want_jetson),
            self.rhandler(BUTTON_DRAW_JETSON, self.ready_but_muted),


            self.rhandler(BUTTON_REFRESH_SCHEDULE, self.not_ready_yet),
            self.rhandler(BUTTON_SEND_INVITES, self.refresh_invites_and_notify),
            self.rhandler(BUTTON_DRAW_PRIZES, self.draw_prizes),
            self.rhandler(BUTTON_DRAW_PRIZES, self.not_ready_yet),
            self.rhandler(BUTTON_POST_NEWS, self.create_broadcast),

            # self.rhandler(BUTTON_ON_MAJOR, self.on_major),

            MessageHandler(Filters.text, self.unknown_command)
        ]}
        return state


def send_notifications(api: TelegramBotApi):
    count = 0

    for user in TGUser.objects.exclude(is_notified=True). \
            exclude(last_checked_email='').exclude(is_authorized=True).all():
        invite = Invite.objects.filter(email=user.last_checked_email).first()
        if invite is not None:
            try:
                api.bot.send_message(user.tg_id, TEXT_INVITE_NOTIFICATION)
                user.is_notified = True
                user.save()
            except Unauthorized:
                logger.info('{} blocked'.format(user))
            count += 1
    return count
