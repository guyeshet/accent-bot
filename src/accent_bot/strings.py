import random
import re

from accent_bot.constants import AccentType
from accent_bot.utils import safe_list_get

EMOJIES = {"usa_flag": "\U0001F1FA\U0001F1F8",
           "uk_flag": "\U0001F1EC\U0001F1E7",
           "world": "\U0001F30E"}

BOT_TEXT = {
    "server_failure": "The server encountered an error",
    "success": ["Well Done!",
                "Excellent Job!",
                "That was awesome!",
                "Great, spot on!"
                ],
    "failure": ["Still not there...",
                "Almost there, try again",
                "Not quite there...",
                "You're making progress! try again..."
                ],
    "welcome": ["Welcome to the Accent Bot!",
                "I'm here to improve your accent {}".format(EMOJIES["world"]),
                ],
    "languages": "Which accent would you like to improve?\n\n"
                 "{} American\n"
                 "{} British".format(EMOJIES["usa_flag"],
                                     EMOJIES["uk_flag"]),
    "language_chosen": "Great! Let's train your {} accent",
    "cancel": "Bye! I hope we continue training one day soon :)"
}

LANGUAGES = ['American', 'British']


def language_regex():
    lang_str = "|".join(LANGUAGES)
    rgx = r'^({})$'.format(lang_str)
    return re.compile(rgx, re.IGNORECASE)


STELLA_SOUND = ["Please call Stella",
                "Ask her to bring these things with her from the store",
                "Six spoons of fresh snow peas",
                "five thick slabs of blue cheese",
                "and maybe a snack for her brother Bob",
                "We also need a small plastic snake",
                "and a big toy frog for the kids",
                "She can scoop these things into three red bags",
                "and we will go meet her Wednesday",
                "at the train station",
                ]


def get_chat_id(context):
    chat_id = safe_list_get(context.job.context, 0, default=0)
    if not chat_id:
        print("missing chat id")

    return chat_id


def get_language(context):
    accent_type = safe_list_get(context.job.context, 1, default=AccentType.USA)
    return AccentType.language(accent_type)


def get_text(name, key=None):
    """
    Return a random value from a list or simply the relevant work
    :param key: a key for the strings dictionary
    :return:
    """
    data = BOT_TEXT[name]
    # in case we already know the sub-location inside a list
    if key is not None:
        data = data[key]
    return random.choice(data) if type(data) == list else data


def success(context, chat_id):
    context.bot.send_message(chat_id=chat_id,
                             text=get_text("success"))


def failure(context, chat_id):
    context.bot.send_message(chat_id=chat_id,
                             text=get_text("failure"))


def server_failure(context, chat_id):
    context.bot.send_message(chat_id=chat_id,
                             text=get_text("server_failure"))


def welcome(context):
    chat_id = get_chat_id(context)
    # get which welcome message it is
    key = safe_list_get(context.job.context, 1, 0)
    context.bot.send_message(chat_id=chat_id,
                             text=get_text("welcome", key))


def get_language_choice(context):
    chat_id = get_chat_id(context)
    # get the chosen language form the context
    text = get_text("language_chosen").format(get_language(context))
    
    context.bot.send_message(chat_id=chat_id,
                             text=text,
                             )
