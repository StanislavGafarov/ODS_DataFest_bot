import logging
from pprint import pformat

from telegram.ext import Updater, Handler, ConversationHandler

from backend.tgbot.base import TelegramBotApi
from backend.tgbot.utils import check_certs, get_public_host, logger
from bot import settings



class SyncBotApi(TelegramBotApi):
    def _patch_handler(self, handler: Handler):
        if not hasattr(handler, '_patched'):
            if isinstance(handler, ConversationHandler):
                def patch_all(handlers):
                    return [self._patch_handler(h) for h in handlers]
                handler.entry_points = patch_all(handler.entry_points)
                handler.states = {name: patch_all(h) for name, h in handler.states.items()}
                handler.fallbacks = patch_all(handler.fallbacks)

            else:
                callback = handler.callback

                def f(bot, update):
                    return callback(self, update)

                handler._patched = True
                handler.callback = f
        return handler

    def start_bot(self, handlers):
        logger.info(pformat(self.bot.getMe()))
        updater = Updater(bot=self.bot, request_kwargs={'con_pool_size': 8})

        for handler in handlers:
            updater.dispatcher.add_handler(self._patch_handler(handler))

        if settings.TG_WEBHOOK:
            check_certs()
            logger.info('Webhook listening at port {}\nInfo at https://api.telegram.org/bot{}/getWebhookInfo'.format(
                settings.TG_WEBHOOK_PORT,
                self.token))
            host = get_public_host()
            updater.start_webhook(listen='0.0.0.0', port=settings.TG_WEBHOOK_PORT,
                                  url_path=self.token,
                                  cert=settings.TG_WEBHOOK_CERT_PEM, key=settings.TG_WEBHOOK_CERT_KEY,
                                  webhook_url='https://{}:{}/{}'.format(host,
                                                                        settings.TG_WEBHOOK_PORT,
                                                                        self.token))
        else:
            logger.info('Start polling')
            updater.start_polling()
