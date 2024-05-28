from flask import Flask, request
import json
import redis
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from pymongo import MongoClient

app = Flask(__name__)

# 连接到MongoDB数据库
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["testdb"]
mongo_collection = mongo_db["user_data"]

# 连接到Redis数据库
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

# Line Bot 设置
access_token = 'Ou03DKB3PDYrfNTrb0+bmaSE8Lt6jo4ArVFmm1PO3qLqtr0tp73Ynzaet2ZIT8vN398tZ1WqRQ3n1oM46JjvUmWAMP7+6pGhvIalX5qmXJsI8G4zlNJMBhWXL6uIVk0/yBNdEdp/2ItNqf/ly4GadAdB04t89/1O/w1cDnyilFU='
secret = '6a9833e4f667e86257c111945b2d2699'
line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

def is_valid_student_id(student_id):
    # 检查学号是否为8位数字
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
        user_id = json_data['events'][0]['source']['userId']  # 获取用户的 Line ID

        # 获取用户的个人资料
        profile = line_bot_api.get_profile(user_id)
        user_name = profile.display_name

        if type == 'text':
            msg = json_data['events'][0]['message']['text']
            print(msg)
            if '學號' in msg:
                # 如果用户发送了包含"學號"关键词的消息，机器人会回复询问用户输入学号
                reply = f"{user_name}，請問您的學號是多少？"
            elif redis_client.hexists(user_id, 'student_id'):
                # 如果 Redis 中已经存在用户的学号，则从 Redis 中获取并回复
                student_id = redis_client.hget(user_id, 'student_id')
                # 将用户的问题存储到 Redis 的列表中并设置10分钟过期
                redis_client.rpush(f"{student_id}_questions", msg)
                redis_client.expire(f"{student_id}_questions", 30)
                reply = f"登入成功！{user_name}，您的學號是 {student_id}，您問的問題是：{msg}。我們會在10分鐘內刪除這條記錄。"
            elif mongo_collection.find_one({"user_id": user_id}):
                # 如果 MongoDB 中已经存在用户的学号，则从 MongoDB 中获取并回复
                user_record = mongo_collection.find_one({"user_id": user_id})
                student_id = user_record['student_id']
                # 将用户的问题存储到 Redis 的列表中并设置10分钟过期
                redis_client.rpush(f"{student_id}_questions", msg)
                redis_client.expire(f"{student_id}_questions", 30)
                reply = f"登入成功！{user_name}，您的學號是 {student_id}，您問的問題是：{msg}。我們會在10分鐘內刪除這條記錄。"
            else:
                if is_valid_student_id(msg):
                    # 将学号和姓名存储到 Redis 和 MongoDB 中
                    redis_client.hset(user_id, mapping={'name': user_name, 'student_id': msg})
                    mongo_collection.insert_one({"user_id": user_id, "name": user_name, "student_id": msg})
                    reply = f"學號已紀錄成功！{user_name}"
                else:
                    reply = "學號格式不正確，請輸入8位數字的學號。"
        else:
            reply = '你傳的不是文字呦～'

        print(reply)

        line_bot_api.reply_message(tk, TextSendMessage(text=reply))
    except Exception as e:
        print(e)
        print(body)
    return 'OK'

if __name__ == "__main__":
    app.run(host='0.0.0.0')
