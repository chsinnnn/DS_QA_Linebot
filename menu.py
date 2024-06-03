from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction, FlexSendMessage
from pymongo import MongoClient
import random
import json
import redis
import requests
from bson.objectid import ObjectId

app = Flask(__name__)

# Line Bot設定
with open('config.json') as config_file:
    config = json.load(config_file)

access_token = config['LINE_ACCESS_TOKEN']
secret = config['LINE_SECRET']

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

# 連MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["testdb"]
mongo_collection = mongo_db["user_data"]

# 連Redis
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

def is_valid_student_id(student_id):
    return student_id.isdigit() and len(student_id) == 8

def handle_student_id(user_id, user_name, msg):
    if is_valid_student_id(msg):
        # 學號格式正確，檢查學號是否已經存在於 MongoDB 中
        existing_user = mongo_collection.find_one({"user_id": user_id})
        if existing_user:
            reply = f"{user_name}，您的學號已經登錄過了。"
        else:
            # 將學號存入 Redis 中
            redis_client.hset(user_id, 'student_id', msg)
            # 同時將學號存入 MongoDB 中
            student_data = {"user_id": user_id, "name": user_name, "student_id": msg}
            mongo_collection.insert_one(student_data)
            reply = f"{user_name}，學號已紀錄成功！請點選表單的我要做答並選題目!!"
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

def handle_question_display(event, unit):  # 多個題目挑選
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
                        "gravity": "center",
                        "color": "#FFFFFF"
                    }
                ]
                #"backgroundColor": "#EBA281"
            },
            #"separator": True,  # 分割線 
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": question["Question"],
                        "wrap": True,
                        "size": "md"
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
            },
            "styles": {
                "header": {
                    "backgroundColor": "#668166" #header底色
                }
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

def handle_question_answer(event, question_title):  # 已選好題目
    question = None
    for unit, collection in unit_collections.items():
        question = collection.find_one({"Question": question_title})
        if question:
            break

    if question:
        user_id = event.source.user_id
        redis_client.hset(user_id, "current_question", question_title)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"請回答以下問題：\n\n{question_title}"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到題目"))

def handle_user_answer(event, user_answer):
    user_id = event.source.user_id
    question_title = redis_client.hget(user_id, "current_question")

    if question_title:
        # 存儲用戶的答案
        redis_client.hset(user_id, "user_answer", user_answer)

        # 從 Redis 中讀取學號
        student_id = redis_client.hget(user_id, "student_id")

        if student_id:
            # 確保題目和答案的鍵存在於 Redis 中
            qa_key = f"{student_id}_qa:{question_title}"

            # 將用戶的答案存儲在列表中
            redis_client.rpush(qa_key, user_answer)
        else:
            # 如果無法找到學號，則拋出錯誤或採取其他適當的處理方式
            print("無法找到學號，無法存儲題目和用戶答案")

        # 將題目發送給 Llama3 伺服器並回傳答案
        llama3_answer = send_question_to_llama3(question_title)

        # 組合要回覆的文字訊息，包括用戶的回答和 Llama3 的回答
        reply_text = f"題目：{question_title}\n\n您回答：{user_answer}\n\nLlama3 回答：{llama3_answer}"

        # 使用 TextSendMessage 回覆文字訊息
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

        # 清除當前題目和用戶回答
        redis_client.hdel(user_id, "current_question")
        redis_client.hdel(user_id, "user_answer")
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="未找到對應的問題，請重新選擇題目。"))

def send_question_to_llama3(question):
    llama3_server_url = 'http://192.168.100.137:5000/ask'

    try:
        print(f"Sending question to Llama3 server: {llama3_server_url}")
        response = requests.post(llama3_server_url, json={'question': question})
        response.raise_for_status()
        answer = response.json().get('answer', '無法獲取回答')
        print(f"Received answer from Llama3 server: {answer}")
        return answer
    except requests.exceptions.RequestException as e:
        print(f"Error sending question to Llama3: {e}")
        return '無法獲取回答'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_profile = line_bot_api.get_profile(user_id)
    user_name = user_profile.display_name

    msg = event.message.text
    if is_valid_student_id(msg):
        reply = handle_student_id(user_id, user_name, msg)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    elif msg == "我要作答":
        if redis_client.hexists(user_id, 'student_id') and mongo_collection.find_one({"user_id": user_id}):
            handle_unit_selection(event)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先輸入學號ㄛ!"))
    elif msg in unit_collections:
        handle_question_display(event, msg)
    elif msg.startswith("回答"):
        if redis_client.hexists(user_id, 'student_id') and mongo_collection.find_one({"user_id": user_id}):
            question_title = msg[2:]
            handle_question_answer(event, question_title)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先輸入學號ㄛ!"))
    elif redis_client.hget(user_id, "current_question"):
        handle_user_answer(event, msg)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="學號格式不正確，請輸入8位數字的學號。"))

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
