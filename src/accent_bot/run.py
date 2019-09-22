import json
import random
import requests
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from accent_bot.utils import from_env

PREDICTION_API = from_env("PREDICTION_API", "http://34.89.217.69:8080")
PREDICTION_URL = PREDICTION_API + "/bot"

HEADERS = {'content-type': 'application/json'}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

STELLA_1 = "Please call Stella.  Ask her to bring these things with her from the store"
STELLA_2 = "Six spoons of fresh snow peas, five thick slabs of blue cheese, and maybe a snack for her brother Bob."
STELLA_3 = "We also need a small plastic snake and a big toy frog for the kids."
STELLA_4 = "She can scoop these things into three red bags, and we will go meet her Wednesday at the train station."


class AccentBot:

    def __init__(self):
        self.text_samples = [STELLA_1, STELLA_2, STELLA_3, STELLA_4]

    def start(self, bot, update):
        text = "Hello! Ask for a new word to learn with /new_word"
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=text)

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

        # puts the received voice in the queue to handle the prediction
        context.job_queue.run_once(AccentBot.handle_prediction, 0, context=[chat_id, voice])

    @staticmethod
    def handle_prediction(context):

        # unpack the context variables
        chat_id, voice = context.job.context
        data = {"path": voice.file_path}

        text = "Waiting for the response"
        context.bot.send_message(chat_id=chat_id, text=text)

        # post the data to the prediction server and wait for response
        r = requests.post(PREDICTION_URL,
                          data=json.dumps(data),
                          headers=HEADERS)

        if not r.ok:
            text = "The server encountered an error, try again"

        else:
            # parse the received response to check prediction status
            response_dict = r.json()
            status = int(response_dict.get("predictions"))

            # 0 is a correct classification
            if status == 0:
                text = "Success!"
            else:
                text = "No there yet... Try again!"

        context.bot.send_message(chat_id=chat_id, text=text)

    def get_word_callback(self, update: Update, context: CallbackContext, args=None):

        text = random.choice(self.text_samples)
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id=chat_id, text=text)


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

    audio_handler = MessageHandler(Filters.voice, accent_bot.receive_voice_message, pass_job_queue=True)
    dp.add_handler(audio_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # Run the bot
    main()

