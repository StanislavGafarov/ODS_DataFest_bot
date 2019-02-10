from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from config import BOT_TOKKEN, APPROVED_EMAIL_LIST

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING = 0
CHECK_EMAIL = 1


def menu(bot, update):
    reply_keyboard = [['Проверить Email', 'Расписание','Подписаться на обновления']]
    # reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text(
        'Привет, че как? '
        'Че делать будем?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CHOOSING


def check_email(bot, update):
    user = update.message.from_user
    text = update.message.text
    logger.info('User {} have chosen {} '.format(user.first_name, text))
    update.message.reply_text('Please type your email, or send /skip if you don\'t want to',
                              reply_markup=ReplyKeyboardRemove())
    return CHECK_EMAIL


def email_in_list(bot, update):
    email = update.message.text
    logger.info('{}'.format(email))
    if email in APPROVED_EMAIL_LIST:
        update.message.reply_text('Fuck yeah, you are in!')
    else:
        update.message.reply_text('Go away looser, you are not in the list')
    return CHOOSING


def table_sheet(bot, update):
    update.message.reply_text('{}'.format('there will be spread sheet with timing'))
    return CHOOSING


def can_spam(bot, update):
    user = update.message.from_user
    chat_id = bot.get_updates()[-1].message.chat_id
    logger.info('User:{}, Chat_id:{} subscribed for notification'.format(user.first_name,chat_id))
    update.message.reply_text('Thank for sub, bro')
    return CHOOSING


def skip_email(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send an email.", user.first_name)
    update.message.reply_text('You seem a bit paranoid!')

    return CHOOSING


def bio(bot, update):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(BOT_TOKKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', menu)],

        states={
            CHOOSING: [RegexHandler('^(Проверить Email)$', check_email),
                   RegexHandler('^(Расписание)$', table_sheet),
                   RegexHandler('^(Подписаться на обновления)$', can_spam)],

            CHECK_EMAIL: [MessageHandler(Filters.text, email_in_list),
                       CommandHandler('skip', skip_email)],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()