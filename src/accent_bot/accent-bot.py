from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Voice
import requests
import re
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

DOWNLOAD_PATH = "../audio"

class AccentBot:

    def __init__(self):
        self.counter = 0

    def get_url(self):
        contents = requests.get('https://random.dog/woof.json').json()
        url = contents['url']
        return url

    def bop(self, bot, update):
        url = self.get_url()
        chat_id = update.message.chat_id
        bot.send_photo(chat_id=chat_id, photo=url)

    def echo(self, bot, update):
        text = update.message.text
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=text)

    def store(self, bot, update):
        voice = update.message.voice.get_file()
        self.counter += 1
        voice.download(DOWNLOAD_PATH + (str)(self.counter))


def main():

    # verify folder exists

    updater = Updater('874455740:AAF-ipcxqBYcvzBkTS16TKLYCPqkPCcytw0')
    dp = updater.dispatcher
    accent_bot = AccentBot()

    dp.add_handler(CommandHandler('bop', accent_bot.bop))

    echo_handler = MessageHandler(Filters.text, accent_bot.echo)
    dp.add_handler(echo_handler)

    audio_handler = MessageHandler(Filters.voice, accent_bot.store)
    dp.add_handler(audio_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()