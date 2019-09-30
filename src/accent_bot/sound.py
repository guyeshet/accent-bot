import os

from accent_bot.utils import get_project_root


def get_sound(num, folder="english128"):
    file_path = os.path.join(get_project_root(),
                             "sound",
                             folder,
                             "stella{}.wav".format(num))
    return file_path