from telegram.ext import ConversationHandler, CommandHandler

from backend.tgbot.tghandler import TGHandler, restore_states

from backend.tgbot.states.main_menu import MainMenu
from backend.tgbot.states.check_registration import CheckRegistrationStatus
from backend.tgbot.states.authorization import Authorization
from backend.tgbot.states.get_news import GetNews
from backend.tgbot.states.broadcasting import Broadcasting

class CustomConversationHandler(TGHandler):

    def get_states(self, *args):
        states = {}
        for obj in args:
            state = obj().create_state()
            states.update(state)
        return states

    def create_handler(self):
        states = self.get_states(MainMenu, CheckRegistrationStatus, Authorization, GetNews, Broadcasting)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states=states,
            fallbacks=[CommandHandler('cancel', self.cancel)],
            allow_reentry=True
        )
        restore_states(conv_handler)
        return [conv_handler]

