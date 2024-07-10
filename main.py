from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction, FlexSendMessage
from pymongo import MongoClient
import random
import json
import redis
import requests
import os
import datetime
from linebot.models import CarouselColumn, TemplateSendMessage, CarouselTemplate

os.chdir('/home/hsin/DS_QA_Linebot')

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
suggestion_collection = mongo_db["suggestions"]
warn_collection = mongo_db['WARN']

# 連Redis
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

special_student_ids = [ '11027149','11027104', '11027133']

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
        db_existing = mongo_collection.find_one({"user_id": user_id})
        red_existing = redis_client.hexists(user_id, 'student_id')
        if db_existing and red_existing:
            reply = f"{user_name}，您的學號已經登錄過了。"
        else:
            # 將學號存入 Redis 中
            redis_client.hset(user_id, 'student_id', msg)
            # 同時將學號存入 MongoDB 中
            student_data = {"user_id": user_id, "name": user_name, "student_id": msg}
            mongo_collection.insert_one(student_data)
            reply = f"{user_name}，學號已紀錄成功！請點選表單的我要作答並選題目!!"
    else:
        reply = "學號格式不正確，請輸入8位數字的學號。"
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
            },
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
                    "backgroundColor": "#668166"  # header底色
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
        # 紀錄回答題目的時間
        answer_submitted_time = datetime.datetime.now().strftime("%Y-%m-%d")

        # 存儲用戶的答案
        redis_client.hset(user_id, "user_answer", user_answer)

        # 從 Redis 中讀取學號
        student_id = redis_client.hget(user_id, "student_id")

        if student_id:
            # 確保題目和答案的鍵存在於 Redis 中
            qa_key = f"{student_id}_qa:{question_title}"
            answer_time_key = f"{student_id}_answer_time:{question_title}"

            # 將用戶的答案存儲在列表中
            redis_client.rpush(qa_key, user_answer)
            redis_client.rpush(answer_time_key, answer_submitted_time)

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

def handle_suggestion(event):
    user_id = event.source.user_id
    suggestion = event.message.text

    if suggestion:
        suggestion_data = {
            "user_id": user_id,
            "suggestion": suggestion
        }
        suggestion_collection.insert_one(suggestion_data)
        redis_client.hdel(user_id, 'awaiting_suggestion')
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="謝謝您的建議！我們會努力改進。"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入您的建議。"))

def send_quick_ans_records_reply(reply_token):
    quick_reply = QuickReply(
        items=[
        QuickReplyButton(action=MessageAction(label="全部", text="查看「全部」的作答紀錄")),
        QuickReplyButton(action=MessageAction(label="其他", text="查看單元「其他」的作答紀錄")),
        QuickReplyButton(action=MessageAction(label="指標", text="查看單元「指標」的作答紀錄")),
        QuickReplyButton(action=MessageAction(label="佇列", text="查看單元「佇列」的作答紀錄")),
        QuickReplyButton(action=MessageAction(label="遞迴", text="查看單元「遞迴」的作答紀錄")),
        QuickReplyButton(action=MessageAction(label="排序", text="查看單元「排序」的作答紀錄")),
        QuickReplyButton(action=MessageAction(label="堆疊", text="查看單元「堆疊」的作答紀錄"))
        ]
    )
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text="選擇要查看作答紀錄的單元", quick_reply=quick_reply)
    )

def show_unit_answer_records(event, student_id, selected_unit):
    # 使用 keys 函數獲取所有與該 student_id 相關的答題時間的 keys
    pattern = f"{student_id}_answer_time:*"
    answer_time_keys = redis_client.keys(pattern)
    question_titles = [key.split(':')[1] for key in redis_client.keys(pattern)]

    # 檢查是否獲取到 keys
    if not answer_time_keys:
        line_bot_api.reply_message(event.reply_token, "沒有找到任何答題記錄。")
    else:
    # 遍歷 keys，獲取並格式化答題時間
        unit_answer_counts = {}
        for key in answer_time_keys:
            answer_times = redis_client.lrange(key, 0, -1)
            question_title = key.split("_answer_time:")[1]

            # 直接使用 question_title_key 查詢，避免不必要的內層循環
            for unit, collection in unit_collections.items():
                if collection.find_one({"Question": question_title}):
                    unit_name = unit
                    if unit_name not in unit_answer_counts:
                        unit_answer_counts[unit_name] = {"count": 0, "times": {}}
                    unit_answer_counts[unit_name]["count"] += len(answer_times)  # 直接增加回答次數
                    for time in answer_times:
                        if time not in unit_answer_counts[unit_name]["times"]:
                            unit_answer_counts[unit_name]["times"][time] = 0
                        unit_answer_counts[unit_name]["times"][time] += 1
                    break  # 找到對應單元後跳出循環

        if selected_unit in unit_answer_counts:
            details = unit_answer_counts[selected_unit]
            units_reply_message = (
                f"單元: {selected_unit} 回答次數: {details['count']} \n答題時間及題數:\n" +
                "".join([f"{time}: {count}題\n" if i < len(list(details['times'].items())) - 1 else f"{time}: {count}題" for i, (time, count) in enumerate(list(details['times'].items()))])
            )
        elif selected_unit == "全部":
            all_units_reply_message = ""
            for unit, details in unit_answer_counts.items():
                times_and_num = "".join([f"{time}: {count}題\n" if i < len(list(details['times'].items())) - 1 else f"{time}: {count}題" for i, (time, count) in enumerate(list(details['times'].items()))])
                # 決定是否在新的單元信息前添加換行符
                if all_units_reply_message == "":  # 如果不是第一個單元，添加換行符
                    unit_message = f"單元: {unit} 回答次數: {details['count']} \n答題時間及題數:\n{times_and_num}"
                else:  # 如果是第一個單元，不在開頭加換行符
                    unit_message = f"\n\n單元: {unit} 回答次數: {details['count']} \n答題時間及題數:\n{times_and_num}"
                
                all_units_reply_message += unit_message

            units_reply_message = all_units_reply_message
        else:
            units_reply_message = f"單元: {selected_unit}\n沒有找到任何答題記錄。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=units_reply_message))

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
    user_document = mongo_collection.find_one({"user_id": user_id})
    student_id = user_document.get("student_id")
    msg = event.message.text
    awaiting_suggestion = redis_client.hget(user_id, 'awaiting_suggestion')
    

    if awaiting_suggestion:
        handle_suggestion(event)
    elif redis_client.hexists(user_id, 'student_id') and mongo_collection.find_one({"user_id": user_id}):
        if msg == "我要作答":
            handle_unit_selection(event)
        elif msg == "歡迎留下您寶貴的建議:D":
            redis_client.hset(user_id, 'awaiting_suggestion', 'true')
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入您的建議。"))
        elif msg in unit_collections:
            handle_question_display(event, msg)
        elif msg.startswith("回答"):
            question_title = msg[2:]
            handle_question_answer(event, question_title)
        elif redis_client.hget(user_id, "current_question"):
            handle_user_answer(event, msg)
        elif msg == "顯示作答紀錄":
            send_quick_ans_records_reply(event.reply_token)
        elif msg.startswith("查看") and msg.endswith("的作答紀錄"):
            # 從消息文本中提取單元名稱
            selected_unit = msg.split("「")[1].split("」")[0]
            # 調用函數顯示該單元的作答紀錄
            show_unit_answer_records(event, student_id, selected_unit)
        elif student_id in special_student_ids:
            if msg == "小提醒":
                send_quick_reply(event.reply_token)
                # 設置標誌以表示用戶現在可以輸入提醒訊息
                redis_client.hset(user_id, 'awaiting_warning_message', 'true')
            elif msg.startswith("刪除提醒"):
                show_warning_messages(event.reply_token)
            elif msg.startswith("刪除:"):
                warning_message = msg.split(':')[1]
                delete_warning_message(warning_message, event.reply_token)
            elif msg == "保留原有提醒":
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入新的提醒"))
                # 重新設置標誌以表示用戶現在可以輸入提醒訊息
                redis_client.hset(user_id, 'awaiting_warning_message', 'true')
            else:
                # 在儲存提醒訊息之前檢查是否真的在等待提醒訊息的輸入
                if redis_client.hget(user_id, 'awaiting_warning_message') == 'true':
                    save_warning_message(msg, event.reply_token)
                    # 清除標誌
                    redis_client.hdel(user_id, 'awaiting_warning_message')
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無效指令，請重新輸入。"))
        elif student_id not in special_student_ids and msg == "小提醒":
            send_warning_message(event.reply_token)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無效指令，請重新輸入。"))
    
    else:
        if is_valid_student_id(msg):
            reply = handle_student_id(user_id, user_name, msg)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先輸入符合格式的學號（8位數字）。"))

def send_quick_reply(reply_token):
    quick_reply_buttons = QuickReply(
        items=[
            QuickReplyButton(action=MessageAction(label="是", text="刪除提醒")),
            QuickReplyButton(action=MessageAction(label="否", text="保留原有提醒")),
        ]
    )
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text="要刪除原有的提醒再加入新的提醒嗎？", quick_reply=quick_reply_buttons)
    )

def show_warning_messages(reply_token):
    warnings = list(warn_collection.find({}))
    if warnings:
        contents = []
        for warning in warnings:
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": warning['message'],
                        "wrap": True,
                        "color": "#000000",
                        "size": "md",
                        "flex": 4
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#EBA281",
                        "action": {
                            "type": "message",
                            "label": f"x",
                            "text": f"刪除:{warning['message']}"
                        },
                    }
                ]
            })
            # 加間隔
            contents.append({
                "type": "separator",
                "margin": "md"
            })

        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "小提醒",
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True,
                        "align": "center",
                        "gravity": "center",
                        "color": "#FFFFFF"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents
            },
            "styles": {
                "header": {
                    "backgroundColor": "#668166" #header底色
                }
            }
        }

        flex_message = FlexSendMessage(
            alt_text="小提醒",
            contents=bubble
        )
        line_bot_api.reply_message(reply_token, flex_message)
    else:
        # 如果沒有提醒可以刪除，提示用戶輸入新的提醒
        line_bot_api.reply_message(reply_token, TextSendMessage(text="目前沒有任何提醒訊息。請輸入新的提醒"))

def delete_warning_message(warning_message, reply_token):
    warn_collection.delete_one({'message': warning_message})
    remaining_warnings = list(warn_collection.find({}))
    if remaining_warnings:
        quick_reply_buttons = QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="是", text="刪除提醒")),
                QuickReplyButton(action=MessageAction(label="否", text="保留原有提醒")),
            ]
        )
        line_bot_api.reply_message(reply_token, TextSendMessage(text="提醒已刪除。您還要刪除其他提醒嗎？如果不刪除，請輸入新的提醒", quick_reply=quick_reply_buttons))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="提醒已刪除。請輸入新的提醒。"))

def save_warning_message(message, reply_token):
    warn_collection.insert_one({"message": message})
    send_warning_message(reply_token)
    ##line_bot_api.reply_message(reply_token, TextSendMessage(text="提醒訊息已儲存。"))

def send_warning_message(reply_token):
    all_warnings = list(warn_collection.find({}))
    if len(all_warnings) > 0:
        warnings = list(warn_collection.find({}))
    if warnings:
        contents = []
        for warning in warnings:
            contents.append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": warning['message'],
                        "wrap": True,
                        "color": "#000000",
                        "size": "md",
                        "flex": 4
                    }
                ]
            })
            # 加間隔
            contents.append({
                "type": "separator",
                "margin": "md"
            })

        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "小提醒",
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True,
                        "align": "center",
                        "gravity": "center",
                        "color": "#FFFFFF"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents
            },
            "styles": {
                "header": {
                    "backgroundColor": "#668166" #header底色
                }
            }
        }

        flex_message = FlexSendMessage(
            alt_text="小提醒",
            contents=bubble
        )
        line_bot_api.reply_message(reply_token, flex_message)
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="目前沒有任何提醒訊息。"))

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
