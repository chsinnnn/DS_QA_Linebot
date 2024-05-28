from flask import Flask, request
import json
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from pymongo import MongoClient

app = Flask(__name__)

# 使用者的 Line ID 作為 key 的字典
user_data = {}

access_token = 'Ou03DKB3PDYrfNTrb0+bmaSE8Lt6jo4ArVFmm1PO3qLqtr0tp73Ynzaet2ZIT8vN398tZ1WqRQ3n1oM46JjvUmWAMP7+6pGhvIalX5qmXJsI8G4zlNJMBhWXL6uIVk0/yBNdEdp/2ItNqf/ly4GadAdB04t89/1O/w1cDnyilFU='
secret = '6a9833e4f667e86257c111945b2d2699'
line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

# 連接到MongoDB數據庫
client = MongoClient("mongodb://localhost:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5")
db = client.testdb
collection = db.user_data

def is_valid_student_id(student_id):
    # 檢查學號是否為8位數字
    return student_id.isdigit() and len(student_id) == 8

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    try:
        json_data = json.loads(body)
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        tk = json_data['events'][0]['replyToken']
        type = json_data['events'][0]['message']['type']
        user_id = json_data['events'][0]['source']['userId']  # 獲取使用者的 Line ID

        # 獲取使用者的個人資料
        profile = line_bot_api.get_profile(user_id)
        user_name = profile.display_name

        if type == 'text':
            msg = json_data['events'][0]['message']['text']
            print(msg)
            if '學號' in msg:
                # 如果使用者發送了包含"學號"關鍵詞的消息，機器人會回覆詢問使用者輸入學號
                reply = f"{user_name}，請問您的學號是多少？"
            elif collection.find_one({"user_id": user_id}):
                # 如果使用者已經提供了學號，回覆登入成功消息，同時顯示使用者的學號
                user_record = collection.find_one({"user_id": user_id})
                student_id = user_record['student_id']
                reply = f"登入成功！{user_name}，您的學號是 {student_id}，請問有什麼可以幫助您的嗎？"
            elif user_id in user_data and user_data[user_id]['student_id'] is None:
                # 如果使用者已經有記錄的學號但還沒有提供學號，則將使用者發送的訊息作為學號存下
                if is_valid_student_id(msg):
                    user_data[user_id]['student_id'] = msg
                    # 將學號存儲到數據庫中
                    collection.insert_one({"user_id": user_id, "name": user_name, "student_id": msg})
                    reply = f"學號已紀錄成功！{user_name}"
                else:
                    reply = "學號格式不正確，請輸入8位數字的學號。"
            elif user_id not in user_data:
                # 如果使用者的學號還未記錄，則提示使用者輸入學號
                reply = f"{user_name}，請先告訴我您的學號哦~"
                # 將使用者的 Line ID 與學號關聯起來
                user_data[user_id] = {'name': user_name, 'student_id': None}
            else:
                reply = msg
        else:
            reply = '你傳的不是文字呦～'

        print(reply)

        # 打印使用者ID與學號字典的內容
        print("使用者ID與學號：", user_data)

        line_bot_api.reply_message(tk, TextSendMessage(text=reply))
    except Exception as e:
        print(e)
        print(body)
    return 'OK'

if __name__ == "__main__":
    app.run(host='0.0.0.0')
