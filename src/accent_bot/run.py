import json
import os
import random
import requests
import logging

from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from accent_bot.strings import success, failure, STELLA_SOUND, BOT_TEXT, welcome, server_failure, \
    get_text, LANGUAGES, get_chat_id, language_regex
from accent_bot.utils import from_env, get_project_root, prediction_url
from accent_bot.constants import AccentType

HEADERS = {'content-type': 'application/json'}

LANGUAGE = "language"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

ACCENT_TYPE, SEND_TEXT, GET_VOICE = range(3)


# def start(update: Update, context: CallbackContext):
    # text = "Hello! Ask for a new word to learn with /new_word"
    # update.message.reply_text(get_text("welcome", 0))
    # chat_id = update.message.chat_id
    # context.bot.send_message(chat_id=chat_id,
    #                          text=get_text("welcome", key))
    # context.job_queue.run_once(welcome, 1, context=[chat_id, 0])
    # context.job_queue.run_once(welcome, 3, context=[chat_id, 1])
    # context.job_queue.run_once(choose_language, 5, context=[chat_id])

    # return ACCENT_TYPE


def choose_language(update: Update, context: CallbackContext):
# def choose_language(context: CallbackContext):
#     chat_id = get_chat_id(context)
    # chat_id = update.message.chat_id
    custom_keyboard = [LANGUAGES]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard,
                                       )
    # context.bot.send_message(chat_id=chat_id,
    #                          text=get_text("languages"),
    #                          reply_markup=reply_markup,
    #                          )
    update.message.reply_text(text=get_text("languages"),
                              reply_markup=reply_markup,)
    return ACCENT_TYPE


def chosen_langauge_response(update: Update, context: CallbackContext):
    user = update.message.from_user
    language = update.message.text

    text = get_text("language_chosen").format(language)
    update.message.reply_text(text=text,
                              reply_markup=ReplyKeyboardRemove()
                              )

    # send a text sample
    return get_word_callback(update, context)


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

    target_language = context.user_data.get(LANGUAGE, AccentType.USA)

    # puts the received voice in the queue to handle the prediction
    context.job_queue.run_once(handle_prediction, 0, context=[chat_id,
                                                              voice,
                                                              target_language])


def handle_prediction(context):

    # unpack the context variables
    chat_id, voice, target_language = context.job.context
    data = {"path": voice.file_path,
            }

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
        success(context, chat_id)
        return SEND_TEXT
    else:
        failure(context, chat_id)
        return GET_VOICE


def get_sound(num, folder="english128"):
    file_path = os.path.join(get_project_root(),
                             "sound",
                             folder,
                             "stella{}.wav".format(num))
    return file_path


def get_word_callback(update: Update, context: CallbackContext, args=None):

    num = random.randint(1, len(STELLA_SOUND))
    text = STELLA_SOUND[num - 1]
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text=text)
    context.bot.send_voice(chat_id=chat_id, voice=open(get_sound(num), 'rb'))

    return GET_VOICE


def set_target_language(update: Update, context: CallbackContext, args=None):
    context.user_data[LANGUAGE] = AccentType.USA
    update.message.reply_text("Let's train your {} accent!".format(context.user_data[LANGUAGE]))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(BOT_TEXT["cancel"],
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():

    # read the config file
    bot_id = from_env("BOT_ID", "XXXX")

    # create the bot updates
    updater = Updater(bot_id, use_context=True)
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', choose_language)],

        states={
            ACCENT_TYPE: [MessageHandler(Filters.regex(language_regex()), chosen_langauge_response)],
            SEND_TEXT: [MessageHandler(Filters.text, get_word_callback)],
            GET_VOICE: [MessageHandler(Filters.voice,
                                       receive_voice_message,
                                       pass_job_queue=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error
                         )
    # # handling communication start
    # dp.add_handler(CommandHandler("start", accent_bot.start))
    #
    # # get the existing
    # dp.add_handler(CommandHandler('text', accent_bot.get_word_callback, pass_args=True))
    # dp.add_handler(CommandHandler('language', accent_bot.set_target_language, pass_args=True))

    # audio_handler = MessageHandler(Filters.voice,
    #                                receive_voice_message,
    #                                pass_job_queue=True)
    # dp.add_handler(audio_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # Run the bot
    main()


