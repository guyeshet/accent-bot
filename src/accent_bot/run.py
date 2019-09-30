import json
import random
import sys

import requests
import logging

from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from accent_bot.strings import STELLA_SOUND, server_failure, \
    get_text, LANGUAGES, language_regex, yes_no_regex, YES_NO
from accent_bot.utils import from_env
from accent_bot.constants import CURRENT_SENTENCE_NUM, INVALID_SENTENCE, CURRENT_LANGUAGE, prediction_url, \
    get_sound_file_path
from accent_bot.common import AccentType

HEADERS = {'content-type': 'application/json'}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

ACCENT_TYPE, WAIT_FOR_START, SEND_TEXT, GET_VOICE = range(4)


def start(update: Update, context: CallbackContext):
    # welcome sequence for a new user
    update.message.reply_text(get_text("welcome", 0))
    update.message.reply_text(get_text("welcome", 1))

    # ask the user to choose the language
    return choose_language(update, context)


def choose_language(update: Update, context: CallbackContext):

    # send a choice keyboard
    custom_keyboard = [LANGUAGES]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard,)

    update.message.reply_text(text=get_text("languages"),
                              reply_markup=reply_markup,)
    return ACCENT_TYPE


def chosen_language_response(update: Update, context: CallbackContext):
    """
    This method is called after the user chose the language
    :param update:
    :param context:
    :return:
    """
    # user = update.message.from_user
    language = update.message.text

    # save the chosen language in the context
    set_language(context, language)

    text = get_text("language_chosen").format(language)
    update.message.reply_text(text=text)

    # send a ready to start button
    update.message.reply_text(text=get_text("ready_to_start"),
                              reply_markup=ReplyKeyboardMarkup([YES_NO])
                              )

    return WAIT_FOR_START


def receive_voice_message(update: Update, context: CallbackContext):
    """
    This method is called every time a voice message is sent
    we will use it to check the accent prediction
    :param update:
    :param context:
    :return:
    """
    # get the voice relevant params
    chat_id = update.message.chat_id

    # details of the voice files (the file url is remote store on telegram)
    voice = update.message.voice.get_file()

    target_language = get_language(context)

    # puts the received voice in the queue to handle the prediction
    # context.job_queue.run_once(handle_prediction, 0, context=[chat_id,
    #                                                           voice,
    #                                                           target_language])
    handle_prediction(update, context, voice, target_language)


def handle_prediction(update: Update, context: CallbackContext, voice, target_language):

    data = {"path": voice.file_path}

    # post the data to the prediction server and wait for response
    r = requests.post(prediction_url(target_language),
                      data=json.dumps(data),
                      headers=HEADERS)

    if not r.ok:
        server_failure(context, chat_id)
        return

    # parse the received response to check prediction status
    response_dict = r.json()
    status = int(response_dict.get("predictions"))

    # 0 is a correct classification
    if status == 0:
        update.message.reply_text("\n\n".join((get_text("success"),
                                               get_text("new_word"))))
        # send a new sentence if the prediction was correct
        set_current_sentence(context, INVALID_SENTENCE)
    else:
        update.message.reply_text(get_text("failure"))

    get_word_callback(update, context)


def set_current_sentence(context, num):
    context.user_data[CURRENT_SENTENCE_NUM] = num


def get_current_sentence(context):
    return context.user_data.get(CURRENT_SENTENCE_NUM, INVALID_SENTENCE)


def set_language(context, lang):
    context.user_data[CURRENT_LANGUAGE] = lang


def get_language(context):
    return context.user_data.get(CURRENT_LANGUAGE, AccentType.USA)


def get_word_callback(update: Update, context: CallbackContext, args=None):
    # check if we need to create a new one
    num = get_current_sentence(context)

    # randomize a new one if needed
    if num == INVALID_SENTENCE:
        num = random.randint(1, len(STELLA_SOUND))
        set_current_sentence(context, num)

    text = STELLA_SOUND[num - 1]
    chat_id = update.message.chat_id

    # send a stella sound sample
    context.bot.send_message(chat_id=chat_id,
                             text="*{}*".format(text),
                             reply_markup=ReplyKeyboardRemove(),
                             parse_mode=ParseMode.MARKDOWN
                             )
    # Send the relevant voice note
    context.bot.send_voice(chat_id=chat_id,
                           voice=open(get_sound_file_path(num,
                                                          get_language(context)), 'rb'))

    return GET_VOICE


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(get_text("cancel"),
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def switch_sentence(update: Update, context: CallbackContext, args=None):
    update.message.reply_text(text=get_text("new_sentence"))
    set_current_sentence(context, INVALID_SENTENCE)
    return get_word_callback(update, context)


def main():

    # read the config file
    bot_id = from_env("BOT_ID", "X")
    if bot_id == "X":
        logger.error("Didn't load Bot ID")
        sys.exit(1)

    # create the bot updates
    updater = Updater(bot_id, use_context=True)
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ACCENT_TYPE: [MessageHandler(Filters.regex(language_regex()), chosen_language_response)],
            WAIT_FOR_START: [MessageHandler(Filters.regex(yes_no_regex()), get_word_callback)],
            SEND_TEXT: [MessageHandler(Filters.text, get_word_callback)],
            GET_VOICE: [MessageHandler(Filters.voice,
                                       receive_voice_message,
                                       pass_job_queue=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel),
                   # Allow the user to switch the language in the conversation
                   CommandHandler('set_language', choose_language),
                   CommandHandler('new_word', switch_sentence),
                   ],
        allow_reentry=True
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error
                         )

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # Run the bot
    main()


