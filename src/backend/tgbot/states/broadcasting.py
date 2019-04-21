import time
from threading import Thread

from telegram.ext import run_async, MessageHandler, Filters, CommandHandler
from telegram.error import Unauthorized

from backend.tgbot.base import TelegramBotApi
from backend.tgbot.tghandler import TGHandler
from backend.tgbot.texts import *
from backend.tgbot.utils import Decorators, logger

from backend.models import TGUser, News


class BroadcastThread(Thread):
    def __init__(self, thread_function):
        super().__init__()
        self.thread_function = thread_function

    def run(self):
        self.thread_function()


class Broadcasting(TGHandler):
    def send_message_to_users(self, api: TelegramBotApi, user_from: TGUser, sender, update):
        def send_impl():
            counter = 0
            error_counter = 0
            for u in TGUser.objects.all():
                try:
                    sender(u.tg_id)
                    counter += 1
                    time.sleep(.1)
                except Unauthorized as err:
                    logger.exception(f'User is unauthorized {u}')
                    u.delete()
                except:
                    logger.exception('Error sending broadcast to user {}'.format(u))
                    error_counter += 1

            api.bot.send_message(self.user.tg_id, TEXT_BROADCAST_DONE.format(counter, error_counter))

        bt = BroadcastThread(send_impl)
        bt.start()
        update.message.reply_text(TEXT_BROADCAST_STARTED, reply_markup=self.define_keyboard(user_from))
        return self.MAIN_MENU

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def send_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        def sender(u):
            api.bot.send_message(u, update.message.text)
        return self.send_message_to_users(api, user, sender, update)

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def send_broadcast_sticker(self, api: TelegramBotApi, user: TGUser, update):
        def sender(u):
            api.bot.send_sticker(u, update.message.sticker.file_id)
        return self.send_message_to_users(api, user, sender, update)

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def send_broadcast_location(self, api: TelegramBotApi, user: TGUser, update):
        def sender(u):
            api.bot.send_location(u, location=update.message.location)
        return self.send_message_to_users(api, user, sender, update)

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def send_broadcast_photo(self, api: TelegramBotApi, user: TGUser, update):
        def sender(u):
            photo = update.message.photo
            if photo:
                api.bot.send_photo(u, photo[0].file_id, update.message.caption)

        return self.send_message_to_users(api, user, sender, update)

    @Decorators.composed(run_async, Decorators.save_msg, Decorators.with_user)
    def cancel_broadcast(self, api: TelegramBotApi, user: TGUser, update):
        logger.info("User {} desided not to send broadcast.", user)
        update.message.reply_text(TEXT_CANCEL_BROADCASTING,
                                  reply_markup=self.define_keyboard(user))
        return self.MAIN_MENU

    def create_state(self):
        state = {self.BROADCAST: [MessageHandler(Filters.text, self.send_broadcast),
                                  MessageHandler(Filters.sticker, self.send_broadcast_sticker),
                                  MessageHandler(Filters.location, self.send_broadcast_location),
                                  MessageHandler(Filters.photo, self.send_broadcast_photo),
                                  CommandHandler('cancel', self.cancel_broadcast)]}
        return state
