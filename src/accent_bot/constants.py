from accent_bot.utils import from_env


class AccentType:
    USA = "American"
    UK = "British"


CURRENT_LANGUAGE = "current_lang"
CURRENT_SENTENCE_NUM = "current_num"
INVALID_SENTENCE = -1

prediction_api = {AccentType.USA: from_env("PREDICTION_API", "http://usa_predictor:8080"),
                  AccentType.UK: from_env("PREDICTION_API", "http://uk_predictor:8080")}


def prediction_url(language):
    api_url = prediction_api[language]
    return "/".join((api_url, "bot"))