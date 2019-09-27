import random

SUCCESS_MESSAGES = ["Well Done!",
                    "Excellent Job!",
                    "That was awesome!",
                    "Great, spot on!"]

FAILURE_MESSAGE = ["Still not there...",
                   "Almost there, try again",
                   "Not quite there...",
                   "You're making progress! try again..."]


def get_message(str_list):
    return random.choice(str_list)


def success_message():
    return get_message(SUCCESS_MESSAGES)


def failure_message():
    return get_message(FAILURE_MESSAGE)