import time
from threading import Thread

from telegram.ext import run_async, MessageHandler, Filters, CommandHandler
from telegram.error import Unauthorized

from backend.tgbot.base import TelegramBotApi
from backend.tgbot.tghandler import TGHandler
from backend.tgbot.texts import *
from backend.tgbot.utils import Decorators, logger

from backend.models import TGUser, Message, News, NEWS_GROUPS


class BroadcastThread(Thread):
    def __init__(self, thread_function):
        super().__init__()
        self.thread_function = thread_function

    def run(self):
        self.thread_function()


class Broadcasting(TGHandler):
    def send_message_to_users(self, api: TelegramBotApi, user_from: TGUser, sender, update, news: News):
        def get_users(news):
            if news.target_group not in NEWS_GROUPS:
                return list()
            group_no = NEWS_GROUPS.index(news.target_group)
            # group_no == 0 is NONE
            if group_no == 1:
                return TGUser.filter(has_news_subscription=True)
            elif group_no == 2:
                return TGUser.filter(is_admin=True)
            elif group_no == 3:
                return TGUser.filter(win_random_prize=True)
            elif group_no == 4:
                return TGUser.objects.all()
            return list()

        def send_impl():
            counter = 0
            error_counter = 0
            users_to = get_users(news)
            count = users_to.count() if users_to else 0
            logger.info(f'Ready to send message to group {news.target_group}, user count {count}')
            for u in users_to:
                try:
                    sender(u.tg_id)
                    counter += 1
                    time.sleep(.1)
                except Unauthorized:
                    logger.exception(f'User is unauthorized {u}')
                    u.delete()
                except:
                    logger.exception('Error sending broadcast to user {}'.format(u))
                    error_counter += 1

            api.bot.send_message(user_from.tg_id, TEXT_BROADCAST_DONE.format(counter, error_counter))

        bt = BroadcastThread(send_impl)
        bt.start()
        update.message.reply_text(TEXT_BROADCAST_STARTED, reply_markup=self.define_keyboard(user_from))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_news)
    def send_broadcast(self, api: TelegramBotApi, user: TGUser, update, news: News):
        def sender(u):
            api.bot.send_message(u, update.message.text)

        news.data_type = 'TEXT'
        news.data = update.message.text
        news.save()
        return self.send_message_to_users(api, user, sender, update, news)

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_news)
    def send_broadcast_sticker(self, api: TelegramBotApi, user: TGUser, update, news: News):
        def sender(u):
            api.bot.send_sticker(u, update.message.sticker.file_id)

        news.data_type = 'STICKER'
        news.data = update.message.sticker.file_id
        news.save()
        return self.send_message_to_users(api, user, sender, update)

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_news)
    def send_broadcast_location(self, api: TelegramBotApi, user: TGUser, update, news: News):
        def sender(u):
            api.bot.send_location(u, location=update.message.location)

        news.data_type = 'LOCATION'
        news.data = 'update.message.location'
        news.save()
        return self.send_message_to_users(api, user, sender, update)

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_news)
    def send_broadcast_photo(self, api: TelegramBotApi, user: TGUser, update, news: News):
        def sender(u):
            photo = update.message.photo
            if photo:
                api.bot.send_photo(u, photo[0].file_id, update.message.caption)

        news.data_type = 'IMAGE'
        news.data = update.message.photo[0].file_id
        news.save()

        return self.send_message_to_users(api, user, sender, update)

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_news)
    def cancel_broadcast(self, api: TelegramBotApi, user: TGUser, update, news: News):
        logger.info(f"User {user} desided not to send broadcast.")
        update.message.reply_text(TEXT_CANCEL_BROADCASTING,
                                  reply_markup=self.define_keyboard(user))
        news.delete()
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_news)
    def back_to_group_select(self, api: TelegramBotApi, user: TGUser, update, news: News):
        update.message.reply_text(TEXT_BROADCAST_CHOOSE_GROUP,
                                  reply_markup=self.broadcast_group_keyboard(user))
        return self.BROADCAST

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user, Decorators.with_news)
    def broadcast_group(self, api: TelegramBotApi, user: TGUser, update, news: News):
        target_group = update.message.text
        if target_group == BUTTON_NEWS_GROUP_WITH_SUBSCRIPTION:
            news.target_group = 'NEWS_SUBSCRIPTION'
        elif target_group == BUTTON_NEWS_GROUP_ADMIN:
            news.target_group = 'ADMINS'
        elif target_group == BUTTON_NEWS_GROUP_WINNERS:
            news.target_group = 'WINNERS'
        elif target_group == BUTTON_NEWS_GROUP_ALL:
            news.target_group = 'ALL'
        else:
            news.target_group = 'NONE'
        news.save()
        logger.info(f"User {user} choosed group {target_group} for broadcast.")
        update.message.reply_text(TEXT_ENTER_BROADCAST,
                                  reply_markup=self.broadcast_message_keyboard(user))
        return self.BROADCAST_TYPE_MESSAGE

    def create_state(self):
        state = {
            self.BROADCAST: [
                self.rhandler(BUTTON_NEWS_GROUP_WITH_SUBSCRIPTION, self.broadcast_group),
                self.rhandler(BUTTON_NEWS_GROUP_ADMIN, self.broadcast_group),
                self.rhandler(BUTTON_NEWS_GROUP_WINNERS, self.broadcast_group),
                self.rhandler(BUTTON_NEWS_GROUP_ALL, self.broadcast_group),
                self.rhandler(BUTTON_FULL_BACK, self.cancel_broadcast),
                MessageHandler(Filters.text, self.unknown_command)
            ],
            self.BROADCAST_TYPE_MESSAGE: [
                MessageHandler(Filters.text, self.send_broadcast),
                MessageHandler(Filters.sticker, self.send_broadcast_sticker),
                MessageHandler(Filters.location, self.send_broadcast_location),
                MessageHandler(Filters.photo, self.send_broadcast_photo),
                self.rhandler(BUTTON_FULL_BACK, self.back_to_group_select),
                CommandHandler('cancel', self.cancel_broadcast)
            ]
        }
        return state
