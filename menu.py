from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction, FlexSendMessage
from pymongo import MongoClient
import random
import json

app = Flask(__name__)

# Line Bot設定
with open('config.json') as config_file:
    config = json.load(config_file)

access_token = config['LINE_ACCESS_TOKEN']
secret = config['LINE_SECRET']

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)


# MongoDB設定
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["testdb"]
unit_collections = {
    "其他": mongo_db["other"],
    "指標": mongo_db["pointer"],
    "佇列": mongo_db["queue"],
    "遞迴": mongo_db["recursion"],
    "排序": mongo_db["sort"],
    "堆疊": mongo_db["stack"]
}

@app.route("/", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_profile = line_bot_api.get_profile(user_id)
    user_name = user_profile.display_name

    if event.message.text == "我要作答":
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="其他", text="其他")),
            QuickReplyButton(action=MessageAction(label="指標", text="指標")),
            QuickReplyButton(action=MessageAction(label="佇列", text="佇列")),
            QuickReplyButton(action=MessageAction(label="遞迴", text="遞迴")),
            QuickReplyButton(action=MessageAction(label="排序", text="排序")),
            QuickReplyButton(action=MessageAction(label="堆疊", text="堆疊"))
            #5/28
        ])

        message = TextSendMessage(text="請選擇一個單元", quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, message)

    elif event.message.text in unit_collections:
        unit = event.message.text
        collection = unit_collections[unit]

        questions = list(collection.find())
        random_questions = random.sample(questions, 5) if len(questions) >= 5 else questions

        bubbles = []
        for question in random_questions:
            bubble = {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "題目",
                            "weight": "bold",
                            "size": "xl",
                            "wrap": True,  # 確保標題文字換行
                            "align": "center",  # 水平居中
                            "gravity": "center"  # 垂直居中
                        }
                    ]
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": question["Question"],
                            "wrap": True,  # 確保內容文字換行
                            "size": "lg"  # 可根據需要調整文字大小
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#EBA281",  # 設置按鈕顏色，例如橙色
                            "action": {
                                "type": "message",
                                "label": f"回答",
                                "text": f"回答{question['Question']}"
                            }
                        }
                    ]
                }
            }
            bubbles.append(bubble)

        flex_message = FlexSendMessage(
            alt_text="選擇題目",
            contents={
                "type": "carousel",
                "contents": bubbles
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)

    elif event.message.text.startswith("回答"):
        question_title = event.message.text[2:]
        question = None
        for unit, collection in unit_collections.items():
            question = collection.find_one({"Question": question_title})
            if question:
                break

        if question:
            flex_message = FlexSendMessage(
                alt_text="題目詳情",
                contents={
                    "type": "bubble",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "題目",
                                "weight": "bold",
                                "size": "xl",
                                "wrap": True,  # 確保標題文字換行
                                "align": "center",  # 水平居中
                                "gravity": "center"  # 垂直居中
                            }
                        ]
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": question["Question"],
                                "wrap": True,  # 確保內容文字換行
                                "size": "lg"  # 可根據需要調整文字大小
                            },
                            {
                                "type": "button",
                                "style": "primary",
                                "color": "#EBA281",  # 設置按鈕顏色，例如橙色
                                "action": {
                                    "type": "message",
                                    "label": "開始作答",
                                    "text": f"開始作答{question['Question']}"
                                }
                            }
                        ]
                    }
                }
            )
            line_bot_api.reply_message(event.reply_token, flex_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到題目"))

if __name__ == "__main__":
    app.run(host='0.0.0.0')