import os

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import yaml

with open('settings.yml') as f:
    SETTINGS = yaml.load(f, Loader=yaml.SafeLoader)

DEBUG = SETTINGS['debug']

if DEBUG:
    from credentials import CHANNEL_SECRET, CHANNEL_ACCESS_TOKEN
else:
    CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
    CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']

app = Flask(__name__)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route('/')
def hello_world():
   return "hello world!"


@app.route('/callback', methods=['POST'])
def callback():
   # get X-Line-Signature header value
   signature = request.headers['X-Line-Signature']

   # get request body as text
   body = request.get_data(as_text=True)
   app.logger.info('Request body: ' + body)

   # handle webhook body
   try:
       handler.handle(body, signature)
   except InvalidSignatureError:
       print("Invalid signature. Please check your channel access token/channel secret.")
       abort(400)

   return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
   line_bot_api.reply_message(
       event.reply_token,
       TextSendMessage(text=event.message.text))


if __name__ == '__main__':
   port = int(os.getenv('PORT', '5000'))
   app.run(host='0.0.0.0', port=port, debug=DEBUG)
