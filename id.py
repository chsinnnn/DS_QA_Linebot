from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction, FlexSendMessage
from pymongo import MongoClient
import random
import json
import redis
import requests

app = Flask(__name__)

# Line Bot設定
with open('config.json') as config_file:
    config = json.load(config_file)

access_token = config['LINE_ACCESS_TOKEN']
secret = config['LINE_SECRET']

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

# 連接到MongoDB數據庫
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["testdb"]
mongo_collection = mongo_db["user_data"]

# 連接到Redis數據庫
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

# MongoDB設定
unit_collections = {
    "其他": mongo_db["other"],
    "指標": mongo_db["pointer"],
    "佇列": mongo_db["queue"],
    "遞迴": mongo_db["recursion"],
    "排序": mongo_db["sort"],
    "堆疊": mongo_db["stack"]
}

# LLaMA3伺服器的API地址
llama3_server_url = "http://llama3-server:5000/evaluate"

def is_valid_student_id(student_id):
    return student_id.isdigit() and len(student_id) == 8

def handle_student_id(user_id, user_name, msg):
    if is_valid_student_id(msg):
        # 學號格式正確，儲存到Redis和MongoDB
        if not redis_client.hexists(user_id, 'student_id'):
            redis_client.hset(user_id, mapping={'name': user_name, 'student_id': msg})
            mongo_collection.insert_one({"user_id": user_id, "name": user_name, "student_id": msg})
            reply = f"學號已紀錄成功！{user_name}"
        else:
            reply = f"{user_name}，您的學號已經登錄過了。"
    else:
        reply = "學號格式不正確，請輸入8位數字的學號。"
    return reply

def handle_question_reply(user_id, user_name, msg):
    if redis_client.hexists(user_id, 'student_id') and mongo_collection.find_one({"user_id": user_id}):
        student_id = redis_client.hget(user_id, 'student_id')
        redis_client.rpush(f"{student_id}_questions", msg)
        redis_client.expire(f"{student_id}_questions", 600)
        reply = f"登入成功！{user_name}，您的學號是 {student_id}"
    else:
        reply = f"{user_name}，請問您的學號是多少呢？"
    return reply

def handle_unit_selection(event):
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="其他", text="其他")),
        QuickReplyButton(action=MessageAction(label="指標", text="指標")),
        QuickReplyButton(action=MessageAction(label="佇列", text="佇列")),
        QuickReplyButton(action=MessageAction(label="遞迴", text="遞迴")),
        QuickReplyButton(action=MessageAction(label="排序", text="排序")),
        QuickReplyButton(action=MessageAction(label="堆疊", text="堆疊"))
    ])

    message = TextSendMessage(text="請選擇一個單元", quick_reply=quick_reply)
    line_bot_api.reply_message(event.reply_token, message)

def handle_question_display(event, unit):
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
                        "wrap": True,
                        "align": "center",
                        "gravity": "center"
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
                        "wrap": True,
                        "size": "lg"
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
                        "color": "#EBA281",
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

def handle_question_answer(event, question_title):
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
                            "wrap": True,
                            "align": "center",
                            "gravity": "center"
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
                            "wrap": True,
                            "size": "lg"
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到題目"))

def evaluate_answer(question, answer):
    payload = {
        "question": question,
        "answer": answer
    }
    try:
        response = requests.post(llama3_server_url, json=payload)
        response.raise_for_status()
        return response.json().get('feedback', '無法取得評估結果')
    except requests.exceptions.RequestException as e:
        return f'評估答案時發生錯誤，請稍後再試。錯誤信息: {str(e)}'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_profile = line_bot_api.get_profile(user_id)
    user_name = user_profile.display_name

    msg = event.message.text

    if '學號' in msg or is_valid_student_id(msg):
        reply = handle_student_id(user_id, user_name, msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    elif msg == "我要作答":
        if redis_client.hexists(user_id, 'student_id') or mongo_collection.find_one({"user_id": user_id}):
            handle_unit_selection(event)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先輸入學號ㄛ!"))
    elif msg in unit_collections:
        handle_question_display(event, msg)
    elif msg.startswith("回答"):
        if redis_client.hexists(user_id, 'student_id') or mongo_collection.find_one({"user_id": user_id}):
            question_title = msg[2:]
            handle_question_answer(event, question_title)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先輸入學號ㄛ!"))
    elif msg.startswith("開始作答"):
        question_title = msg[4:]
        answer = msg[len(question_title) + 4:]
        question = None
        for unit, collection in unit_collections.items():
            question = collection.find_one({"Question": question_title})
            if question:
                break
        if question:
            # Save question and answer to Redis in JSON format
            student_id = redis_client.hget(user_id, 'student_id')
            qa_data = json.dumps({"question": question["Question"], "answer": answer})
            redis_client.rpush(f"{student_id}_qa", qa_data)
            redis_client.expire(f"{student_id}_qa", 600)
            
            feedback = evaluate_answer(question["Question"], answer)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=feedback))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到問題。"))
    else:
        reply = handle_question_reply(user_id, user_name, msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@app.route("/", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

if __name__ == "__main__":
    app.run(host='0.0.0.0')
