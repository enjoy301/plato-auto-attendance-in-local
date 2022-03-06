from slack_sdk import WebClient
import yaml
import datetime


class SlackApi:
    def __init__(self, token):
        self.client = WebClient(token)

    def post_message(self, text):
        result = self.client.chat_postMessage(
            channel="#plato-attendance-check-notice",
            text=text,
        )

        return result

def main(messages):
    with open('./secrets.yml') as yml:
        config = yaml.load(yml, Loader=yaml.BaseLoader)
        bot_token = config['bot-token']

    slack = SlackApi(token=bot_token)
    for message in messages:
        slack.post_message(message)
