import json
import random

import requests
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from accent_bot.utils import get_credentials

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

PREDICTION_URL = "http://35.198.123.215:8080/bot"
HEADERS = {'content-type': 'application/json'}


class AccentBot:

    def __init__(self):
        self.dictionary = {'abc': 0, '1,2,3' : 0, 'xyz' : 0}
        self.audio_samples = ['abc.oga', '1,2,3.oga', 'xyz.oga']
        self.word = None

    def start(self, bot, update):
        text = "Hello! Ask for a new word to learn with /new_word"
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=text)

    def echo(self, bot, job):
        raise NotImplemented

    def receive_voice_message(self, bot, update, job_queue):
        """
        This method is called every time a voice message is sent
        we will use it to check the accent prediction
        :param bot:
        :param update:
        :param job_queue:
        :return:
        """
        # get the voice relevant params
        chat_id = update.message.chat_id
        # details of the voice files (the file url is remote store on telegram)
        voice = update.message.voice.get_file()

        # puts the received voice in the queue to handle the prediction
        job_queue.run_once(self.handle_prediction, 0, context=[chat_id, voice])

    def handle_prediction(self, bot, job):

        # unpack the context variables
        chat_id, voice = job.context
        data = {"path": voice.file_path}

        text = "Waiting for the response"
        bot.send_message(chat_id=chat_id, text=text)

        # post the data to the prediction server and wait for response
        r = requests.post(PREDICTION_URL,
                          data=json.dumps(data),
                          headers=HEADERS)

        # parse the received response to check prediction status
        response_dict = r.json()
        status = int(response_dict.get("predictions"))

        # 0 is a correct classification
        if status == 0:
            text = "Success!"
        else:
            text = "No there yet... Try again!"

        bot.send_message(chat_id=chat_id, text=text)

    def get_word(self):
        rand_word, attempt = random.choice(list(self.dictionary.items()))
        return rand_word

    def get_audio(self):
        audio = "../audio/" + self.word + ".oga"
        return audio

    def get_word_callback(self, bot, update, args=None):
        if args is None:
            word = self.get_word()
        else:
            word = args[0]
        self.word = word
        audio = self.get_audio()
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=self.word)
        bot.send_voice(chat_id=chat_id, voice=open(audio, 'rb'))


def get_bot_id():
    """
    read a json formatted credentials json and return to bot id
    :return bot_id:
    """
    # TODO - find a general location for the credentials file
    data = get_credentials()
    return data["bot_id"]


def main():

    # read the config file
    bot_id = get_bot_id()

    # create the bot updates
    updater = Updater(bot_id)

    dp = updater.dispatcher
    accent_bot = AccentBot()

    # handling communication start
    dp.add_handler(CommandHandler("start", accent_bot.start))

    # ask for a new word
    dp.add_handler(CommandHandler('new_word', accent_bot.get_word_callback, pass_args=False))

    # get the existing
    dp.add_handler(CommandHandler('get_word', accent_bot.get_word_callback, pass_args=True))

    audio_handler = MessageHandler(Filters.voice, accent_bot.receive_voice_message, pass_job_queue=True)
    dp.add_handler(audio_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # Run the bot
    main()
