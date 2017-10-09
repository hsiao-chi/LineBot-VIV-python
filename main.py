#!/usr/bin/env python
# coding: utf-8

from gae_http_client import RequestsHttpClient

from google.appengine.api import taskqueue

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import config
import datetime
import calendar

app = Flask(__name__)

line_bot_api = LineBotApi(config.CHANNEL_ACCESS_TOKEN, http_client=RequestsHttpClient)
handler = WebhookHandler(config.CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Task Queue Add
    taskqueue.add(url='/worker',
                  params={'body': body,
                          'signature': signature},
                  method="POST")

    return 'OK'

@app.route("/worker", methods=['POST'])
def worker():
    body = request.form.get('body')
    signature = request.form.get('signature')

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    msg = msg.encode('utf-8')
    date=datetime.datetime.now().date()
    if msg=="#日期":
        d = date.year+" 年 "+date.month+" 月 "+date.day+" 日 "
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=d))
    if msg=="#月曆":
        cal = calendar.month(date.year, date.month)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text=cal))
    if msg=="hi" or "你好":
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="郁：10月要好好加油呢! "+msg))
    
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=msg))




if __name__ == "__main__":
    app.run()
