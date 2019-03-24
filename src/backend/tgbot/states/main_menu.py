from telegram.ext import run_async
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from backend.tgbot.utils import logger, save_msg, with_user, rhandler
from backend.models import Invite, TGUser
from backend.tgbot.base import TelegramBotApi
from backend.tgbot.texts import *
from backend.tgbot.handlers import CHECK_REGISTRATION_STATUS, AUTHORIZATION

MAIN_MENU = 1
# CHECK_REGISTRATION_STATUS = 2
# AUTHORIZATION = 3

#Keyboards
ADMIN_KEYBOARD = [BUTTON_REFRESH_SCHEDULE, BUTTON_SEND_INVITES, BUTTON_START_RANDOM_PRIZE, BUTTON_POST_NEWS]
AUTHORIZED_USER_KEYBOARD = [BUTTON_SCHEDULE, BUTTON_NEWS, BUTTON_SHOW_PATH,
                            BUTTON_PARTICIPATE_IN_RANDOM_PRIZE, BUTTON_RANDOM_BEER]
UNAUTHORIZED_USER_KEYBOARD = [BUTTON_CHECK_REGISTRATION, BUTTON_AUTHORISATION, BUTTON_SCHEDULE,
                              BUTTON_NEWS, BUTTON_SHOW_PATH]

def make_keyboard(user: TGUser):
    if user.is_admin:
        keyboard = ADMIN_KEYBOARD
    elif user.is_authorized:
        keyboard = AUTHORIZED_USER_KEYBOARD
    else:
        keyboard = UNAUTHORIZED_USER_KEYBOARD
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)



@run_async
@save_msg
@with_user
def check_registration_status(api: TelegramBotApi, user: TGUser, update):
    text = update.message.text
    logger.info('User {} have chosen {} '.format(user, text))
    update.message.reply_text(TEXT_ENTER_EMAIL, reply_markup=ReplyKeyboardRemove())
    return CHECK_REGISTRATION_STATUS

@run_async
@save_msg
@with_user
def authorization(api: TelegramBotApi, user: TGUser, update):
    text = update.message.text
    logger.info('User {} have chosen {} '.format(user, text))
    update.message.reply_text(TEXT_ENTER_EMAIL, reply_markup=ReplyKeyboardRemove())
    return AUTHORIZATION

########## Не авторизованный ##########
# Проверить статус регистрации
# Авторизоваться
# TODO: Показать расписание
# TODO: Подписаться на новости феста / Новости феста
# TODO: Подсказка как добраться
########## Авторизованный ##########
# TODO: Показать расписание
# TODO: Подписаться на новости феста / Новости феста
# TODO: Подсказка как добраться
# TODO: Учавствовать в розыгрыше
# TODO: Учавстваовать в random_beer
########## Админ ##########
# TODO: Обновить расписание
# TODO: Разослать инвайты
# TODO: Запостить новость
# TODO: Запустить розыгрыш

# TODO: add to handlers
'''
{MAIN_MENU: [
    rhandler(BUTTON_CHECK_REGISTRATION, check_registration_status),
    rhandler(BUTTON_AUTHORISATION, authorization)

    # 
    # rhandler(BUTTON_CHECK_EMAIL, check_email),
    # rhandler(BUTTON_SCHEDULE, show_schedule),
    # rhandler(BUTTON_REGISTRATION, can_spam),
    # rhandler(BUTTON_POST_NEWS, create_broadcast)
    # rhandler(BUTTON_POST_NEWS, create_broadcast)
]}
'''