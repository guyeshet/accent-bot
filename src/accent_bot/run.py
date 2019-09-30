import json
import os
import random
import requests
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from accent_bot.strings import success, failure, STELLA_SOUND, BOT_TEXT, welcome, choose_language, server_failure, \
    get_language_choice
from accent_bot.utils import from_env, get_project_root, prediction_url
from accent_bot.constants import AccentType

HEADERS = {'content-type': 'application/json'}

LANGUAGE = "language"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class AccentBot:

    def __init__(self):
        self.text_samples = STELLA_SOUND
        self.chosen_accent = AccentType.USA

    def start(self, update: Update, context: CallbackContext):
        # text = "Hello! Ask for a new word to learn with /new_word"
        chat_id = update.message.chat_id
        context.job_queue.run_once(welcome, 1, context=[chat_id, 0])
        context.job_queue.run_once(welcome, 3, context=[chat_id, 1])
        context.job_queue.run_once(choose_language, 5, context=[chat_id])

        # needs to happen after the callaback from choose languages
        # context.job_queue.run_once(get_language_choice, 7, context=[chat_id, self.chosen_accent])

    def echo(self, bot, job):
        raise NotImplemented

    # def receive_voice_message(self, bot, update, job_queue):
    @staticmethod
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
        context.job_queue.run_once(AccentBot.handle_prediction, 0, context=[chat_id,
                                                                            voice,
                                                                            target_language])

    @staticmethod
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
        else:
            failure(context, chat_id)

    @staticmethod
    def get_sound(num, folder="english128"):
        file_path = os.path.join(get_project_root(),
                                 "sound",
                                 folder,
                                 "stella{}.wav".format(num))
        return file_path

    def get_word_callback(self, update: Update, context: CallbackContext, args=None):

        num = random.randint(1, len(self.text_samples))
        text = self.text_samples[num - 1]
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id=chat_id, text=text)
        context.bot.send_voice(chat_id=chat_id, voice=open(self.get_sound(num), 'rb'))

    def set_target_language(self, update: Update, context: CallbackContext, args=None):

        context.user_data[LANGUAGE] = AccentType.USA
        update.message.reply_text("Let's train your {} accent!".format(context.user_data[LANGUAGE]))


def main():

    # read the config file
    bot_id = from_env("BOT_ID", "XXXX")

    # create the bot updates
    updater = Updater(bot_id, use_context=True)
    dp = updater.dispatcher
    accent_bot = AccentBot()

    # handling communication start
    dp.add_handler(CommandHandler("start", accent_bot.start))

    # get the existing
    dp.add_handler(CommandHandler('text', accent_bot.get_word_callback, pass_args=True))
    dp.add_handler(CommandHandler('language', accent_bot.set_target_language, pass_args=True))

    audio_handler = MessageHandler(Filters.voice,
                                   accent_bot.receive_voice_message,
                                   pass_job_queue=True)
    dp.add_handler(audio_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # Run the bot
    main()


