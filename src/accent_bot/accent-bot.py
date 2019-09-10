import json
import random

import requests
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from accent_bot.HelloEcho import Hello

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

hello = Hello()

url = "http://35.198.123.215:8080/bot"

class AccentBot:

    def __init__(self):
        self.dictionary = {'abc': 0, '1,2,3' : 0, 'xyz' : 0}
        self.audio_samples = ['abc.oga', '1,2,3.oga', 'xyz.oga']
        self.word = None

    def start(self, bot, update):
        text = "Hello! Ask for a new word to learn with /new_word"
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=text)

    # def get_url(self):
    #     contents = requests.get('https://random.dog/woof.json').json()
    #     url = contents['url']
    #     return url

    # used for checking the run of the bot

    # def set_dictionary(self, accent):
    # set the dictionaries based on the urls?


    def echo(self, bot, job):
        # text = update.message.text
        # chat_id = update.message.chat_id
        # bot.send_message(chat_id=chat_id, text=text)
        text = hello.echo(self.word)
        bot.send_message(chat_id=job.context, text=text)

    def store(self, bot, update, job_queue):
        # if(self.word is not None):
        chat_id = update.message.chat_id
        # needs a new name to be stored by
        # word_attempt = self.word + '_' + (str)(self.dictionary[self.word])
        # self.dictionary[self.word] += 1
        # audio_name = "../attempts/" + word_attempt + ".oga"
        # voice.download(audio_name)

        job_black_box = job_queue.run_once(self.request, 0, context=chat_id)


    def request(self, bot, job):

        voice = update.message.voice.get_file()
        headers = {'content-type': 'application/json'}
        data = {"path": voice.file_path}
        r = requests.post(url, data=json.dumps(data), headers=headers)

        text = "Waiting for the response"
        bot.send_message(chat_id=chat_id, text=text)

        text = r.json()
        text = text.get("predictions")
        if (int(text) == 0):
            text = "Success!"
        else:
            text = "You suck! Try again!"

        bot.send_message(chat_id=chat_id, text=text)

    def get_word(self):
        # rand_item = self.dictionary[random.randrange(len(self.dictionary))]
        rand_word, attempt = random.choice(list(self.dictionary.items()))
        return rand_word

    def get_audio(self):
        audio = "../audio/" + self.word + ".oga"
        return audio

    def getWord(self, bot, update, args=None):
        if args is None:
            word = self.get_word()
        else:
            word = args[0]
        self.word = word
        audio = self.get_audio()
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=self.word)
        bot.send_voice(chat_id=chat_id, voice=open(audio, 'rb'))

def main():
    updater = Updater('874455740:AAF-ipcxqBYcvzBkTS16TKLYCPqkPCcytw0')

    dp = updater.dispatcher
    accent_bot = AccentBot()

    dp.add_handler(CommandHandler("start", accent_bot.start))

    dp.add_handler(CommandHandler('new_word', accent_bot.getWord, pass_args=False))
    dp.add_handler(CommandHandler('get_word', accent_bot.getWord, pass_args=True))

    # echo_handler = MessageHandler(Filters.text, accent_bot.echo)
    # dp.add_handler(echo_handler)

    audio_handler = MessageHandler(Filters.voice, accent_bot.store, pass_job_queue=True)
    dp.add_handler(audio_handler)

    # once the user sends the voice,
    # we send it to the "black box"
    # once the black box gives us result we ping it to the user
    # Ask Guy

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
