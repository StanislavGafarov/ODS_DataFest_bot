import traceback
from abc import abstractmethod

import telegram
import telegram.utils.request
from cached_property import cached_property

from backend.models import TGUser
from bot import settings


class TelegramBotApi:
    def __init__(self, token):
        self.token = token

    @cached_property
    def bot(self) -> telegram.Bot:
        if settings.TG_USE_PROXY and settings.TG_PROXY_ADDRESS:
            request_kwargs = {
                'proxy_url': settings.TG_PROXY_ADDRESS,

            }
            if settings.TG_PROXY_USERNAME is not None:
                proxy_auth = {
                    'username': settings.TG_PROXY_USERNAME,
                    'password': settings.TG_PROXY_PASSWORD,
                    'cert_reqs': None
                }
                if settings.TG_PROXY_ADDRESS.startswith('socks'):
                    request_kwargs['urllib3_proxy_kwargs'] = proxy_auth
                else:
                    request_kwargs.update(proxy_auth)

            request = telegram.utils.request.Request(**request_kwargs)
        else:
            request = None

        bot = telegram.Bot(self.token, request=request)

        return bot

    @abstractmethod
    def start_bot(self, handlers):
        pass

    def get_user_data(self, user_id):
        chat = self.bot.get_chat(user_id)
        return chat.username or '', chat.first_name or '', chat.last_name or ''

    def update_user_data(self, user: 'TGUser'):
        try:
            username, name, last_name = self.get_user_data(user.tg_id)
            user.last_name = last_name
            user.name = name
            user.username = username
        except:
            print('Error getting user data')
            traceback.print_exc()
        user.save()

    def get_user(self, tg_id):
        user = TGUser.objects.filter(tg_id=tg_id).first()
        if user is None:
            user = TGUser(tg_id=tg_id)  # todo More Data
            user.save()
        if user.last_name == '' and user.name == '' and user.username == '':
            self.update_user_data(user)
        return user
