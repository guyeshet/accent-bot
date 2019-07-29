import random

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Voice
import requests
import re
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class AccentBot:

    def __init__(self):
        self.dictionary = {'abc': 0, '1,2,3' : 0, 'xyz' : 0}
        self.audio_samples = ['abc.oga', '1,2,3.oga', 'xyz.oga']
        self.word = None

    # def get_url(self):
    #     contents = requests.get('https://random.dog/woof.json').json()
    #     url = contents['url']
    #     return url

    # used for checking the run of the bot

    # def set_dictionary(self, accent):
    # set the dictionaries based on the urls?


    def echo(self, bot, update):
        text = update.message.text
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=text)

    def store(self, bot, update):
        if(self.word is not None):
            voice = update.message.voice.get_file()
            # needs a new name to be stored by
            word_attempt = self.word + '_' + (str)(self.dictionary[self.word])
            self.dictionary[self.word] += 1
            voice.download("../audio/" + word_attempt + ".oga")
            chat_id = update.message.chat_id
            text = "Waiting for the response"
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

    dp.add_handler(CommandHandler('new_word', accent_bot.getWord, pass_args=False))
    dp.add_handler(CommandHandler('get_word', accent_bot.getWord, pass_args=True))

    echo_handler = MessageHandler(Filters.text, accent_bot.echo)
    dp.add_handler(echo_handler)

    audio_handler = MessageHandler(Filters.voice, accent_bot.store)
    dp.add_handler(audio_handler)

    # once the user sends the voice,
    # we send it to the "black box"
    # once the black box gives us result we ping it to the user
    # Ask Guy

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
