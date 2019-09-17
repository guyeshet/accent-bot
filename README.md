# accent-bot

This bot is intended for accent classification as part of the IDC Deep Learning course.
The bot determines whether a voice message is read in an American accent or not.

Use the docker-compose environment located in [accent_training_deployment](https://github.com/guyeshet/accent_training_deployment)
Make sure you set the bot credentials in **credentials.json** file

To run the bot, run the following command
```shell
pip install -r requirements.txt
python accent_bot/run.py
```

