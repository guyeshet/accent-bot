import logging
import os

from accent_bot.common import AccentType
from accent_bot.utils import from_env, get_project_root

logger = logging.getLogger(__name__)

CURRENT_LANGUAGE = "current_lang"
CURRENT_SENTENCE_NUM = "current_num"
INVALID_SENTENCE = -1

prediction_api = {AccentType.USA: from_env("PREDICTION_API", "http://usa_predictor:8080"),
                  AccentType.UK: from_env("PREDICTION_API", "http://uk_predictor:8080")}


def prediction_url(language):
    api_url = prediction_api[language]
    return "/".join((api_url, "bot"))


SOUND_FOLDERS = {AccentType.USA: "english128",
                 AccentType.UK: "english128"}


def get_sound_file_path(num, language):
    # Get the relevant base folder with a USA default
    sound_folder = SOUND_FOLDERS.get(language)
    if not sound_folder:
        sound_folder = SOUND_FOLDERS[AccentType.USA]
        logger.error("Couldn't load sound folder, using default value")

    file_path = os.path.join(get_project_root(),
                             "sound",
                             sound_folder,
                             "stella{}.wav".format(num))
    return file_path

