# coding: utf-8
import os 
import sys
import json
from dotenv import load_dotenv

import base64
import hashlib
import hmac

from flask import Flask, request, abort
from linebot import (
    LineBotApi
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    TextSendMessage,
)


app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
    
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)

def base64url_decode(target):
    rem = len(target) % 4
    if rem > 0:
        target += '=' * (4 - rem)

    return base64.urlsafe_b64decode(target)

@app.route('/')
def get():
    return "Hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    signature_decoded = base64url_decode(signature)

    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 署名検証
    hash = hmac.new(channel_secret.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()
    validation_signature = hmac.compare_digest(signature_decoded, hash)
    # 署名検証が通ったらリクエストボディの中からWebhookイベントのリストを取り出す
    if validation_signature:
        events = json.loads(body)['events']
    else:
        abort(400)


    # メッセージイベントでかつテキストメッセージである場合は受け取ったテキストをそのまま返信する(それ以外はスルー)
    for event in events:
        if event is None:
            continue
        if event['type'] != "message" or event['message']['type'] != 'text':
            continue

        line_bot_api.reply_message(
            event['replyToken'],
            TextSendMessage(text=event['message']['text'])
        )

    return 'OK'

if __name__ == "__main__":
    app.run(debug=True, port=5000)
