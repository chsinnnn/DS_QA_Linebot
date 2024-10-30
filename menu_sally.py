from flask import Flask, request, abort, jsonify
import yagmail
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction, FlexSendMessage
from pymongo import MongoClient
import random
import json
import redis
import requests
import os
from linebot import AsyncLineBotApi
from linebot.models import FlexSendMessage, StickerMessage, StickerSendMessage
os.chdir('/home/hsin/DS_QA_Linebot')
from linebot.models import ImageSendMessage
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import glob
import time
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Line Bot設定
with open('config.json') as config_file:
    config = json.load(config_file)

access_token = config['LINE_ACCESS_TOKEN']
secret = config['LINE_SECRET']

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

# 使用 AsyncApiClient
#async_api = AsyncLineBotApi(access_token=access_token)

# 連MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["testdb"]
mongo_db_question = mongo_client["teststudentdata"]
collection_class1 = mongo_db_question["firstclass"]# 各班級的集合
collection_class2 = mongo_db_question["secondclass"]# 各班級的集合
collection_other = mongo_db_question["other"]# 各班級的集合
mongo_db_student1 = mongo_client["student_class1"]
mongo_db_student2 = mongo_client["student_class2"]
mongo_db_student3 = mongo_client["student_other"]
#student_ans = mongo_db2["student_ans"]
mongo_collection = mongo_db["user_data"]
suggestion_collection = mongo_db["suggestions"]
warn_collection = mongo_db['WARN']

#mongo_client.drop_database("student_other")


# 連Redis
redis_host = 'localhost'
redis_port = 6379 
redis_db = 0
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

#redis_client.flushdb()
#print("Redis 資料庫已成功清空。")

special_student_ids = []

# MongoDB設定
unit_collections = {
    "其他": mongo_db["other"],
    "指標": mongo_db["pointer"],
    "佇列": mongo_db["queue"],
    "遞迴": mongo_db["recursion"],
    "排序": mongo_db["sort"],
    "堆疊": mongo_db["stack"],
    "二元樹": mongo_db["bst"]
}

def is_valid_student_id(student_id):
    return student_id.isdigit() and len(student_id) == 8

def handle_student_id(user_id, user_name, msg):
    if is_valid_student_id(msg):
        # 學號格式正確，檢查學號是否已經存在於 MongoDB 中
        db_existing = mongo_collection.find_one({"user_id": user_id})
        red_existing = redis_client.hexists(user_id, 'student_id')
        if db_existing and red_existing:
            reply = "您的學號已經登錄過了。請輸入「密碼」"
        else:
            # 將學號存入 Redis 中
            redis_client.hset(user_id, 'student_id', msg)
            # 同時將學號存入 MongoDB 中
            student_data = {"user_id": user_id, "name": user_name, "student_id": msg}
            mongo_collection.insert_one(student_data)
            reply = "學號已紀錄成功！請輸入「密碼」"
    else:
        reply = "學號格式不正確，請輸入8位數字的「學號」"
    return reply

def check_usage_time(student_id):
    # 取得目前的日期和時間
    current_datetime = datetime.now()
    current_time = current_datetime.time()
    current_date = current_datetime.date()

    # 定義需要的日期（例如：10/29）
    required_date = datetime.strptime("2024-10-29", "%Y-%m-%d").date()

    # 定義班級的使用時間區段
    class_times = {
        #"甲班": (datetime.strptime("10:00", "%H:%M").time(), datetime.strptime("12:00", "%H:%M").time()),
        #"乙班": (datetime.strptime("15:00", "%H:%M").time(), datetime.strptime("17:00", "%H:%M").time()),
    }

    # 從 mongo_collection 中查詢學生的班級
    student_data = mongo_collection.find_one({"student_id": student_id})
    class_name = student_data.get("class") if student_data else None
    print(f"學生 {student_id} 的班級是 {class_name}")

    # 判斷是否在允許的時間內
    if class_name in class_times:
        # 判斷日期是否符合
        if current_date != required_date:
            print("當前日期不符合要求")
            return False
        start_time, end_time = class_times[class_name]
        if start_time <= current_time <= end_time:
            return True
    else:
        return True
    
    return False
    
def handle_unit_selection(event):
    quick_reply = QuickReply(items=[
        
        QuickReplyButton(action=MessageAction(label="指標", text="指標")),
        QuickReplyButton(action=MessageAction(label="佇列", text="佇列")),
        QuickReplyButton(action=MessageAction(label="遞迴", text="遞迴")),
        QuickReplyButton(action=MessageAction(label="排序", text="排序")),
        QuickReplyButton(action=MessageAction(label="堆疊", text="堆疊")),
        QuickReplyButton(action=MessageAction(label="二元樹", text="二元樹")),
        QuickReplyButton(action=MessageAction(label="其他", text="其他"))
    ])

    message = TextSendMessage(text="請選擇一個單元", quick_reply=quick_reply)
    line_bot_api.reply_message(event.reply_token, message)


def handle_question_insert(event):
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "DS管理系統",
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
                    "type": "button",
                    "style": "primary",
                    "color": "#EBA281",
                    "height": "sm",  # 設置按鈕的高度為 "sm" 來縮小按鈕
                    "size": "sm",    # 設置按鈕的大小為 "sm" 來縮小按鈕
                    "action": {
                        "type": "uri",
                        "label": "點我",
                        "uri": "https://question.lab214b.uk:5001/"  # 確保這個 URL 是公開可訪問的
                    }
                }
            ]
        },
        "styles": {
            "header": {
                "backgroundColor": "#668166"
            }
        }
    }

    # 使用正確的內容格式創建 FlexSendMessage
    flex_message = FlexSendMessage(
        alt_text="題目管理",
        contents=bubble  # 不需要將 bubble 包裝成列表
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

def handle_question_display(event, unit, student_id):  # 多個題目挑選
    collection = unit_collections[unit]

    # 查詢學生班級
    student_record = mongo_collection.find_one({"student_id": student_id})

    # 根據查詢結果選擇集合
    if student_record:
        class_name = student_record.get("class")
        if class_name == "甲班":
            student_collection = mongo_db_student1
        elif class_name == "乙班":
            student_collection = mongo_db_student2
        else:
            student_collection = mongo_db_student3
    else:
        student_collection = mongo_db_student3

    # 獲取學生已回答過的題目
    student_answers = list(student_collection[student_id].find({"unit": unit}))
    answered_questions = {data["question_title"] for answer in student_answers for data in answer["student_data"]}

    # 獲取所有題目並過濾掉已回答過的題目
    questions = list(collection.find({"Question": {"$nin": list(answered_questions)}}))
    random_questions = random.sample(questions, 3) if len(questions) >= 3 else questions

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
                            "text": f"我要回答:\n{question['Question']}"
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

    if bubbles:
        flex_message = FlexSendMessage(
            alt_text="選擇題目",
            contents={
                "type": "carousel",
                "contents": bubbles
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    else:  # 如果已完成該單元的所有題目
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你已完成這個單元的所有題目！"))

def handle_question_answer(event, student_id, question_title):  # 已選好題目
    question = None
    for unit, collection in unit_collections.items():
        question = collection.find_one({"Question": question_title})
        if question:
            found_collection = unit
            break

    # 查詢學生班級
    student_record = mongo_collection.find_one({"student_id": student_id})

    # 根據查詢結果選擇集合
    if student_record:
        class_name = student_record.get("class")
        if class_name == "甲班":
            student_collection = mongo_db_student1
        elif class_name == "乙班":
            student_collection = mongo_db_student2
        else:
            student_collection = mongo_db_student3
    else:
        student_collection = mongo_db_student3

    if question:
        user_id = event.source.user_id
        # 檢查用戶是否已經回答過該問題
        existing_answer = student_collection[student_id].find_one(
            {"unit": found_collection, "student_data.question_title": question_title}
        )

        if existing_answer:
            # 回覆用戶已經回答過該問題
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="你已經回答過這題了！！！\n請繼續選擇其他題目作答哦"))
        else:
            # 將選擇的問題存入 Redis，供後續使用
            redis_client.hset(user_id, "current_question", question_title)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"請回答以上你所選的問題\n(回答100字以下)"))
    else:
        # 若未找到問題，回覆錯誤訊息
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到題目"))


def handle_user_answer(event, user_answer, student_id):
    user_id = event.source.user_id

    user_answer = user_answer.replace('\n', '').replace('\r', '').strip()

    if len(user_answer) > 100:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="回答字數過多，請重新點選開始作答"))
        redis_client.hdel(user_id, 'current_question')
        return

    special_keywords = {
        "我要作答": lambda event: handle_unit_selection(event),
        "歡迎留下您寶貴的建議:D": lambda event: handle_awaiting_suggestion(event),
        "顯示作答紀錄": lambda event: show_unit_answer_records(event, student_id),
        "小提醒": lambda event: send_warning_message(event.reply_token)
    }

    # 檢查用戶輸入是否為特殊指令
    if user_answer in special_keywords:
        special_keywords[user_answer](event)
        # 跳出回答題目模式
        redis_client.hdel(user_id, 'current_question')
        return

    question_title = redis_client.hget(user_id, "current_question")

    if question_title:
        # 紀錄回答題目的時間
        #answer_submitted_time = datetime.datetime.now().strftime("%Y-%m-%d")

        # 存儲用戶的答案
        redis_client.hset(user_id, "user_answer", user_answer)

        # 從 Redis 中讀取學號
        student_id = redis_client.hget(user_id, "student_id")
        #redis_key = f"{question_title}_answers"

        #if student_id:
            # 確保題目和答案的鍵存在於 Redis 中
            #qa_key = f"{student_id}_qa:{question_title}"
            #answer_time_key = f"{student_id}_answer_time:{question_title}"
            #score_key = f"{student_id}_score:{question_title}"

            # 將用戶的答案存儲在列表中
            #redis_client.rpush(qa_key, user_answer)
            #redis_client.rpush(answer_time_key, answer_submitted_time)

        #else:
            # 如果無法找到學號，則拋出錯誤或採取其他適當的處理方式
            #print("無法找到學號，無法存儲題目和用戶答案")

        # 假設 Question 是一個字典，裡面有 "question_title"
        Question = {
            "question": question_title
        }

        # 取出題目的標題
        questions = Question["question"]

    # 遍歷每一個 collection
    found = False
    for category, collection in unit_collections.items():
        # 從當前的 collection 中查詢符合題目標題的文件（改為查詢 "Question" 字段）
        result = collection.find_one({"Question": questions})
        
        # 如果找到了結果，打印出對應的類別和答案
        if result:
            question_type = result.get("Type", "")
            answers = result.get("Answer", ["未找到答案"])
            formatted_answers = ',\n'.join([f'"{answer}"' for answer in answers])
            
            found_collection = category
            found = True

            qa_key = f"{question_title}"
            #redis_client.rpush(qa_key, user_answer)

        # 定義生成星星圖案的函數
            def generate_star_rating(score):
                # 確保 score 是整數
                try:
                    score = int(score)  # 將 score 轉換為整數
                except ValueError:
                    score = 0  # 如果轉換失敗，設置為 0（或其他預設值）
                
                # 根據分數生成星星
                return "★" * score + "☆" * (3 - score)  # 3 為滿分
            
            # 使用 json.loads 轉換為 Python 列表
            if isinstance(answers, str):
                answers = json.loads(answers)

            # 去除學生答案的前後空格
            stripped_user_answer = user_answer.strip().replace(" ", "")
            # 檢查題目類型
            if question_type == "封閉式問題(有標準答案)":
                # 直接比對學生回答與標準答案（也去除標準答案的前後空格並移除所有空格）
                if any(stripped_user_answer == ans.strip().replace(" ", "") for ans in answers):
                    answer = {"score": 3, "comment": "回答正確"}
                else:
                    answer = {"score": 0, "comment": "答案不正確"}
                print(stripped_user_answer)
                print(answers)

            
            # 如果是開放式問題，則照原本處理
            else:
                if len(stripped_user_answer) >= 10:
                    previous_answers = redis_client.lrange(qa_key, 0, -1)
                    if stripped_user_answer in previous_answers:
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="此答案已經有人回答過!"))
                        return  # 不存入資料庫，也不進行後續處理
                    
                # 如果沒有重複答案，則將答案存入 Redis 中
                redis_client.rpush(qa_key, stripped_user_answer)

                reply = f'"question"："{question_title}",\n"student_answer"："{user_answer}",\n"reference_answer": [\n{formatted_answers}\n]'
                print(reply)
                # 將題目發送給 語言模型並回傳答案 
                answer = send_question_to_mymodel(reply, event)
                print(answer)

            # 根據評分生成星星圖案
            star_rating = generate_star_rating(answer['score'])

            # 組合要回覆的文字訊息，包括用戶的回答和語言模型評論
            reply_text = f"評分: {star_rating} ({answer['score']})\n評論: {answer['comment']}\n\n如果在使用上有任何問題或建議歡迎填寫表單告訴我們謝謝!\nhttps://forms.gle/CKkcN63ujV53cNhv5"
                
            # 建立學生回答資料
            student_answer_data = {
                "學號": student_id,
                "評分": int(answer['score']),
                "答案": user_answer,
                "評語": answer['comment']
            }

            # 查詢學生班級
            student_record = mongo_collection.find_one({"student_id": student_id})

            # 根據查詢結果選擇集合
            if student_record:
                class_name = student_record.get("class")
                if class_name == "甲班":
                    collection = collection_class1
                    student_collection = mongo_db_student1
                elif class_name == "乙班":
                    collection = collection_class2
                    student_collection = mongo_db_student2
                else:
                    collection = collection_other
                    student_collection = mongo_db_student3
            else:
                # 若找不到該學生記錄，預設放入其他
                collection = collection_other
                student_collection = mongo_db_student3

            # 查詢問題是否已存在於資料庫中
            existing_question = collection.find_one({"Question": question_title})

            if existing_question:
                # 如果問題已存在，將學生回答新增到 `studentans_score`
                existing_question["studentans_score"].append(student_answer_data)
                    
                # 更新平均分數
                existing_question["平均分數"] = calculate_average_score(existing_question["studentans_score"])
                    
                # 更新資料庫中的問題資料
                collection.update_one({"Question": question_title}, {"$set": existing_question})

            else:
                # 如果問題不存在，則建立一個新的問題資料
                new_question = {
                    "Question": question_title,
                    "studentans_score": [student_answer_data],
                    "平均分數": calculate_average_score([student_answer_data])
                }
                collection.insert_one(new_question)

            data = {
                "question_title": question_title,
                "student_answer": user_answer,
                "student_score": answer['score']
            }

            new_student_data = {
                "unit": found_collection,
                "student_data": [data]
            }

            # 查詢該學生是否已經有此單元的回答記錄
            existing_unit = student_collection[student_id].find_one({"unit": found_collection})

            if existing_unit:
                # 如果該單元已存在，將新回答的資料加入到現有的 student_data 陣列中
                student_collection[student_id].update_one(
                    {"unit": found_collection},
                    {"$push": {"student_data": data}}
                )
            else:
                # 如果該單元不存在，插入新的記錄
                student_collection[student_id].insert_one(new_student_data)
             
            # 使用 TextSendMessage 回覆文字訊息
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
            
            # 清除當前題目和用戶回答
            redis_client.hdel(user_id, "current_question")
            redis_client.hdel(user_id, "user_answer")
            break

    # 如果未找到對應的問題，則給出提示
    if not found:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="未找到對應的問題，請重新選擇題目。"))

def calculate_average_score(student_scores): # 計算平均分數
    total_score = sum(student["評分"] for student in student_scores)
    if len(student_scores) > 0:
        return total_score / len(student_scores)
    return 0

def handle_suggestion(event, student_id):
    user_id = event.source.user_id
    suggestion = event.message.text
    yag = yagmail.SMTP(user='linechattt@gmail.com', password='synf wuxi bzwj qcqq')
    special_keywords = {
        "我要作答": handle_unit_selection,
        "歡迎留下您寶貴的建議:D": handle_awaiting_suggestion,
        "顯示作答紀錄": lambda event: show_unit_answer_records(event, student_id),
        "小提醒": lambda event: send_warning_message(event.reply_token)
    }

    if suggestion in special_keywords:
        special_keywords[suggestion](event)
        # 如果是 "歡迎留下您寶貴的建議:D"，設置標誌表示進入意見回饋模式
        if suggestion == "歡迎留下您寶貴的建議:D":
            redis_client.hset(user_id, 'awaiting_suggestion', 'true')
        else:
            # 跳出意見回饋模式
            redis_client.hdel(user_id, 'awaiting_suggestion')
    else:
        # 檢查是否在等待意見回饋
        awaiting_suggestion = redis_client.hget(user_id, 'awaiting_suggestion')
        if awaiting_suggestion:
            # 儲存意見回饋數據
            suggestion_data = {
                "user_id": user_id,
                "student_id": student_id,  # 儲存學號
                "suggestion": suggestion
            }
            suggestion_collection.insert_one(suggestion_data)
            redis_client.hdel(user_id, 'awaiting_suggestion')
            
            # 設定語言模型API的URL
            model_api_url = "http://192.168.100.140:3000/generate"  # 替換為語言模型伺服器的IP地址和端口號

            # 準備發送到語言模型API的數據
            payload = {
                "input_text": suggestion  # 確認API接收的字段名為 'input_text'
            }

            try:
                # 發送POST請求到語言模型API
                response = requests.post(model_api_url, json=payload)
                
                # 檢查請求是否成功
                if response.status_code == 200:
                    # 解析API回覆的JSON數據
                    data = response.json()
                    model_reply = data.get("output", "模型未能生成回覆")
                    # 發送回覆給使用者
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=model_reply))
                else:
                    print(f"Error: Received status code {response.status_code}")
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="模型回覆失敗，請稍後再試。"))
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="謝謝您的回饋 ！"))
                #本來是連不上模型伺服器的話，就回覆謝謝您的回饋
             # 發送意見到電子郵件
            try:
                subject = f"來自學生 {student_id} 的意見回饋"
                body = f"學號: {student_id}\n意見回饋: {suggestion}"
                yag.send(to='linechattt@gmail.com', subject=subject, contents=body)
                print("Suggestion email sent successfully！")
            except Exception as e:
                print(f"Failed to send email: {e}")

            redis_client.hdel(user_id, 'awaiting_suggestion')
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入有效的指令或意見回饋。"))

def handle_admin_view_suggestions(event):
    suggestions = list(suggestion_collection.find())
    
    if len(suggestions) == 0:
        line_bot_api.reply_message(event.reply_token, [TextSendMessage(text="目前沒有任何意見回饋。")])
        return
    
    # 排除重複內容
    unique_suggestions = []
    seen_suggestions = set()
    for suggestion in suggestions:
        student_id = suggestion.get("student_id", "未知")
        suggestion_text = suggestion.get("suggestion", "無內容")
        if suggestion_text not in seen_suggestions:
            seen_suggestions.add(suggestion_text)
            unique_suggestions.insert(0, {
                "student_id": student_id,
                "suggestion": suggestion_text
            })
    
    # 分組，每5筆回饋組成一張卡片
    grouped_suggestions = [unique_suggestions[i:i + 5] for i in range(0, len(unique_suggestions), 5)]

    bubbles = []
    
    for group in grouped_suggestions:
        body_contents = []
        for item in group:
            body_contents.append({
                "type": "text",
                "text": f"學號 : {item['student_id']}\n意見 : {item['suggestion']}",
                "wrap": True,
                "size": "md"
            })
            # 在每條意見之後添加一個 separator
            body_contents.append({
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
                        "text": "意見回饋",
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
                "contents": body_contents
            },
            "styles": {
                "header": {
                    "backgroundColor": "#668166"  # header底色
                }
            }
        }
        bubbles.append(bubble)

    # 只回應前 5 張卡片
    if len(bubbles) > 5:
        bubbles = bubbles[:5]

    # 創建Flex訊息，組成carousel結構
    flex_message = FlexSendMessage(
        alt_text="意見回饋",
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )

    line_bot_api.reply_message(event.reply_token, flex_message)

def handle_awaiting_suggestion(event):
    user_id = event.source.user_id
    redis_client.hset(user_id, 'awaiting_suggestion', 'true')
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入您的建議。"))


def create_unit_bubble(unit_name, details):

    bubble = {
      "type": "bubble",
      "size": "micro",
      "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": f"單元 : {unit_name}",
            "color": "#ffffff",
            "align": "start",
            "size": "md",
            "gravity": "center"
          },
          {
            "type": "text",
            "text": f"{details['answer_percentage']}%",
            "color": "#ffffff",
            "align": "start",
            "size": "xs",
            "gravity": "center",
            "margin": "lg"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "filler"
                  }
                ],
                "width": f"{details['answer_percentage']}%",
                "backgroundColor": "#EBA281",
                "height": "6px"
              }
            ],
            "backgroundColor": "#FFFFFF",
            "height": "6px",
            "margin": "sm"
          }
        ],
        "backgroundColor": "#668166",
        "paddingTop": "19px",
        "paddingAll": "12px",
        "paddingBottom": "16px"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": f"目前回答題數: {details['count']}",
                "size": "sm"
              }
            ]
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "button",
                "action": {
                  "type": "message",
                  "label": "分數分布",
                  "text": f"查看{unit_name}的分數分布"
                },
                "color": "#F9F2DC",
                "style": "secondary"
              }
            ]
          }
        ],
        "spacing": "md",
        "paddingAll": "12px"
      },
      "styles": {
        "footer": {
          "separator": False
        }
      }
    }
    return bubble

def create_no_record_bubble():
    return {
      "type": "bubble",
      "size": "deca",
      "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "color": "#ffffff",
            "align": "center",
            "size": "md",
            "gravity": "center",
            "text": "❗❗❗"
          },
          {
            "type": "text",
            "align": "center",
            "text": "你還沒回答任何問題",
            "size": "lg",
            "gravity": "center",
            "color": "#F9F2DC",
            "margin": "none",
            "weight": "bold"
          }
        ],
        "backgroundColor": "#668166",
        "paddingTop": "19px",
        "paddingAll": "12px",
        "paddingBottom": "16px"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "button",
                "action": {
                  "type": "message",
                  "label": "我要作答",
                  "text": "我要作答"
                },
                "color": "#000000",
                "size": "lg",

              }
            ],
            "backgroundColor": "#F9F2DC",
            "borderWidth": "none",
            "alignItems": "center",
            "cornerRadius": "xxl"
          }
        ],
        "spacing": "md",
        "paddingAll": "12px"
      },
      "styles": {
        "footer": {
          "separator": True
        }
      }
    }

def show_unit_answer_records(event, student_id):
    # 查詢學生班級
    student_record = mongo_collection.find_one({"student_id": student_id})

    # 根據查詢結果選擇集合
    if student_record:
        class_name = student_record.get("class")
        if class_name == "甲班":
            student_collection = mongo_db_student1
        elif class_name == "乙班":
            student_collection = mongo_db_student2
        else:
            student_collection = mongo_db_student3
    else:
        student_collection = mongo_db_student3

    # 查詢這個學生在 MongoDB 中的所有回答記錄
    student_answers = list(student_collection[student_id].find())

    if not student_answers:
        no_record_bubble = create_no_record_bubble()
        flex_message = FlexSendMessage(alt_text="沒有答題記錄", contents={"type": "carousel", "contents": [no_record_bubble]})
        line_bot_api.reply_message(event.reply_token, flex_message)
    else:
        unit_answer_counts = {}
        unit_total_counts = {}

        # 計算每個單元的總題數
        for unit, collection in unit_collections.items():
            total_questions = collection.count_documents({})
            unit_total_counts[unit] = total_questions

        # 用於追蹤已經計算過的問題
        calculated_questions = set()

        for answer_record in student_answers:
            unit_name = answer_record["unit"]

            for data in answer_record["student_data"]:
                question_title = data["question_title"]

                # 如果問題已經計算過，跳過
                if question_title in calculated_questions:
                    continue

                if unit_name not in unit_answer_counts:
                    unit_answer_counts[unit_name] = {"count": 0, "times": {}}
                unit_answer_counts[unit_name]["count"] += 1  # 每個問題只計算一次

                answer_time = data.get("answer_time")
                if answer_time:
                    if answer_time not in unit_answer_counts[unit_name]["times"]:
                        unit_answer_counts[unit_name]["times"][answer_time] = 0
                    unit_answer_counts[unit_name]["times"][answer_time] += 1

                # 標記問題為已計算
                calculated_questions.add(question_title)

        # 計算每個單元的回答題數百分比
        for unit, counts in unit_answer_counts.items():
            total_questions = unit_total_counts.get(unit, 0)
            answered_questions = counts["count"]
            if total_questions > 0:
                answer_percentage = (answered_questions / total_questions) * 100
            else:
                answer_percentage = 0
            # 取到小數點後一位
            unit_answer_counts[unit]["answer_percentage"] = round(answer_percentage, 1)

        bubbles = []
        for unit, details in unit_answer_counts.items():
            details["total_questions"] = unit_total_counts.get(unit, 0)
            bubbles.append(create_unit_bubble(unit, details))

        flex_message = FlexSendMessage(alt_text="答題記錄", contents={"type": "carousel", "contents": bubbles})
        line_bot_api.reply_message(event.reply_token, flex_message)

def calculate_score_distribution(unit_name, student_id):
    # 初始化分數分佈字典
    score_distribution = {0: 0, 1: 0, 2: 0, 3: 0}
    
    # 查詢學生班級
    student_record = mongo_collection.find_one({"student_id": student_id})

    # 根據查詢結果選擇集合
    if student_record:
        class_name = student_record.get("class")
        if class_name == "甲班":
            student_collection = mongo_db_student1
        elif class_name == "乙班":
            student_collection = mongo_db_student2
        else:
            student_collection = mongo_db_student3
    else:
        student_collection = mongo_db_student3

    # 獲取該學生在 MongoDB 中的所有回答記錄
    student_answers = list(student_collection[student_id].find({"unit": unit_name}))

    # 遍歷學生的回答記錄，統計每個分數的數量
    for answer_record in student_answers:
        for data in answer_record["student_data"]:
            score = data.get("student_score")  # 獲取學生分數
            if score in score_distribution:
                score_distribution[score] += 1  # 增加對應分數的計數

    # 返回分數分佈
    return score_distribution


def plot_score_distribution(unit_name, score_distribution, file_path):
    scores = list(score_distribution.keys())
    counts = list(score_distribution.values())
    simhei_font = FontProperties(fname='/usr/share/fonts/SimHei.ttf')
    # 繪製摺線圖
    plt.plot(scores, counts, marker='o', linestyle='-', color='#668166', zorder=5, clip_on=False)

    # 設定 X 軸和 Y 軸標籤
    plt.xlabel('分數', fontproperties=simhei_font, fontsize=14)
    plt.ylabel('作答題數', fontproperties=simhei_font, fontsize=14)
    plt.title(f'{unit_name} 分數分布圖', fontproperties=simhei_font, fontsize=16)

    # 設定 X 軸和 Y 軸刻度為整數
    plt.xticks(scores)  # 使用分數作為 X 軸刻度
    max_y = max(3, max(counts) + 1)  # 若 counts 最大值超過 3，則使用 max(counts) + 1 作為上限
    plt.yticks(range(0, max_y + 1))  # Y 軸範圍基於最大值，取整數

    # 移除圖表的上邊界和右邊界的線條，只保留 X 和 Y 軸
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 設定 X 軸和 Y 軸的線條顏色為黑色
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_color('black')

    # 設定 X 軸和 Y 軸的 0 點重合
    ax.spines['left'].set_position(('data', 0))
    ax.spines['bottom'].set_position(('data', 0))

    # 設定 X 軸和 Y 軸的範圍
    ax.set_xlim(0, max(scores) + 0.25)  # 增加邊界以容納虛線
    ax.set_ylim(0, max_y)  # 根據 max_y 設定 Y 軸範圍

    # 設定 X 軸和 Y 軸的網格線 (使用 #668166 色的虛線)
    plt.grid(which='both', axis='both', color='#668166', linestyle='--', linewidth=0.5, zorder=1)

    # 限制虛線不超出 XY 軸範圍
    ax.set_axisbelow(True)

    # 保存圖表
    plt.savefig(file_path)
    plt.close()

def calculate_and_send_score_distribution(event, unit_name, student_id):
    # 計算分數分佈
    score_distribution = calculate_score_distribution(unit_name, student_id)
    
    # 圖片儲存路徑
    image_path = f'/home/hsin/DS_QA_Linebot/web/static/{student_id}_score_distribution.jpg'
    
    # 生成分數分佈圖
    plot_score_distribution(unit_name, score_distribution, image_path)
    
    # 將圖表傳送給使用者
    image_url = f'https://question.lab214b.uk:5001/static/{student_id}_score_distribution.jpg'
    
    line_bot_api.reply_message(
        event.reply_token,
        ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
        )
    )

def delete_old_jpg_files():
    # 圖片儲存路徑
    path = '/home/hsin/DS_QA_Linebot/web/static/*.jpg'
    files = glob.glob(path)
    current_time = time.time()
    
    for f in files:
        # 獲取圖片的最後修改時間
        file_time = os.path.getmtime(f)
        
        # 如果圖片超過 24 小時（1 天）未更新，則刪除
        if (current_time - file_time) > 24 * 3600:  # 24 小時 = 1 天
            os.remove(f)
            print(f"Deleted: {f}")

scheduler = BackgroundScheduler()
# 每 3 小時檢查一次，將超過 24 小時未更新的圖片刪除
scheduler.add_job(func=delete_old_jpg_files, trigger='interval', hours=3)
scheduler.start()
        
def send_question_to_mymodel(question, event):
    # 設定語言模型API的URL
    model_api_url = "http://192.168.100.140:5001/generate"  # 替換為語言模型伺服器的IP地址和端口號

    # 準備發送的數據
    payload = {
        "input_text": question  # 修改這裡的鍵名為 input_text，符合API預期的字段
    }

    try:
        # 發送POST請求到語言模型的API，設定超時為60秒
        response = requests.post(model_api_url, json=payload, timeout=60)
        # 檢查請求是否成功
        if response.status_code == 200:
            # 解析回覆的JSON數據
            data = response.json()
            score = data.get("score", "未提供評分")
            comment = data.get("comment", "未提供評論")
            
            # 返回結果作為字典
            return {"score": score, "comment": comment}
        elif response.status_code == 500:
            print("模型格式錯誤")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="模型格式錯誤"))
        else:
            print(f"Error: Received status code {response.status_code}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="模型回覆失敗，請稍後再試。"))
    except requests.exceptions.Timeout:
        print("模型回應超時")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="模型回應超時，請稍後再試。"))
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="無法連接到模型伺服器。"))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_id = event.source.user_id
    user_profile = line_bot_api.get_profile(user_id)
    user_name = user_profile.display_name
    user_document = mongo_collection.find_one({"user_id": user_id})
    student_id = None if user_document is None else user_document.get("student_id")
    msg = event.message.text
    awaiting_suggestion = redis_client.hget(user_id, 'awaiting_suggestion')
    student_account = redis_client.hget(user_id, 'student_account')
    awaiting_password = redis_client.hget(user_id, 'awaiting_password')

    if awaiting_suggestion:
        handle_suggestion(event, student_id)
    elif student_account:
        if msg == "我要作答" and student_id not in special_student_ids:
            if check_usage_time(student_id): #檢查是否在使用時間
                handle_unit_selection(event)
            else:
                message = TextSendMessage(text="目前不是使用時間，請在特定使用時間做使用")
                line_bot_api.reply_message(event.reply_token, message)
        elif msg == "我要作答" and student_id in special_student_ids :  #老師助教
            handle_question_insert(event)
        elif msg == "歡迎留下您寶貴的建議:D":
            if student_id in special_student_ids:
                handle_admin_view_suggestions(event)
            else:
                handle_awaiting_suggestion(event)
        elif msg in unit_collections:  #學生
            handle_question_display(event, msg, student_id)
        elif msg.startswith("我要回答:"):
            question_title = msg[6:]
            if check_usage_time(student_id): #檢查是否在使用時間
                handle_question_answer(event, student_id, question_title)
            else:
                message = TextSendMessage(text="目前不是使用時間，請在特定使用時間做使用")
                line_bot_api.reply_message(event.reply_token, message)
        elif redis_client.hget(user_id, "current_question"):
            handle_user_answer(event, msg, student_id)
        elif msg == "顯示作答紀錄":
            if student_id in special_student_ids:
                handle_question_insert(event)
            else:
                show_unit_answer_records(event, student_id)
        elif msg.startswith('查看') and msg.endswith('分數分布'):
            unit_name = msg[2:-5]
            calculate_and_send_score_distribution(event, unit_name, student_id)
        elif student_id in special_student_ids:
            if msg == "小提醒":
                show_warning_messages(event.reply_token)
                # 設置標誌以表示用戶現在可以輸入提醒訊息
                redis_client.hset(user_id, 'awaiting_warning_message', 'true')
            elif msg.startswith("刪除提醒"):
                show_warning_messages(event.reply_token)
            elif msg.startswith("新增提醒"):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入新的提醒"))
                # 重新設置標誌以表示用戶現在可以輸入提醒訊息
                redis_client.hset(user_id, 'awaiting_warning_message', 'true')
            elif msg.startswith("查看提醒"):
                send_warning_message(event.reply_token)
                redis_client.hdel(user_id, 'awaiting_warning_message')
            elif msg.startswith("結束"):
                send_warning_message(event.reply_token)
                # 清除標誌
                redis_client.hdel(user_id, 'awaiting_warning_message')  
            elif msg.startswith("刪除 :"):
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
    elif awaiting_password :
        student_password = msg
        account = {
            "student_id": student_id,
            "password": student_password,  
        }
        check_account(account, user_name, user_id, event)

    else:
        if is_valid_student_id(msg):
            reply = handle_student_id(user_id, user_name, msg)
            redis_client.hset(user_id, 'awaiting_password', 'true')
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="輸入符合格式的「學號」！\n（8位數）"))
# 貼圖
stickers = {
    446: [1988, 2027],
    789: [10855, 10894],
    1070: [17839, 17878],
    6136: [10551376, 10551399],
    6325: [10979904, 10979927],
    6359: [11069848, 11069871],
    6632: [11825374, 11825398],
    11538: [51626494, 51626533]
}


@handler.add(MessageEvent, message=StickerMessage)
def reply_sticker_message(event: MessageEvent):
    choice = random.choice(list(stickers.keys()))
    reply = StickerSendMessage(package_id=choice, sticker_id=random.choice(
        range(stickers[choice][0], stickers[choice][1] + 1)))
    line_bot_api.reply_message(event.reply_token, reply)


# 使用 Tab 分隔符讀取文件，並清理欄位名稱的空白字符
class_a_df = pd.read_csv('/home/hsin/DS_QA_Linebot/甲班.csv', encoding='utf-16', sep='\t')
class_b_df = pd.read_csv('/home/hsin/DS_QA_Linebot/乙班.csv', encoding='utf-16', sep='\t')
class_a_df.columns = class_a_df.columns.str.strip()
class_b_df.columns = class_b_df.columns.str.strip()

def add_class_info_to_db(user_id, user_name, student_id, mongo_collection):
    # 檢查學生是否在甲班或乙班的學號列表中
    if student_id in class_a_df['學號'].astype(str).values:
        class_name = '甲班'
    elif student_id in class_b_df['學號'].astype(str).values:
        class_name = '乙班'
    else:
        class_name = '其他'
    
    # 更新資料庫中的資料
    mongo_collection.update_one(
        {"user_id": user_id}, 
        {
            "$set": {
                "name": user_name,
                "student_id": student_id,
                "class": class_name
            }
        }
    )

def check_account(account, user_name, user_id, event):
    # 發送 POST 請求
    response = requests.post("http://192.168.100.141:4000/login", json=account)

    # 打印回傳的 JSON 資料
    print(response.json())
    # 解析回傳的 JSON 資料
    response_data = response.json()

    # 如果 success 為 True，更新 Redis 中的 student_account 值為 True
    if response_data.get("success") or account["student_id"] == account["password"]:
        redis_client.hset(user_id, 'student_account', 'true')
        redis_client.hset(user_id, 'awaiting_password', 'false')
        add_class_info_to_db(user_id, user_name, account["student_id"], mongo_collection) # 確認學生班級並存入資料庫
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="登入成功！請點選選單的「我要作答」並選擇題目！！！"))
    else:
        print("Login failed or returned false.")
        # 刪除 Redis 中的資料
        redis_client.delete(user_id)
        # 刪除 MongoDB 中的資料
        mongo_collection.delete_one({"user_id": user_id})
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="錯誤！！！請重新輸入「學號」"))

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
                            "text": f"刪除 :{warning['message']}"  # 按下按鈕會發送此訊息
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
            "footer": {
                "type": "box",
                "layout": "horizontal",  # 水平佈局
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "color": "#F9F2DC",
                        "action": {
                            "type": "message",
                            "label": "新增提醒",
                            "text": "新增提醒"  # 按下按鈕會發送此訊息
                        },
                        "flex": 1,
                        "margin": "md"  # 增加按鈕的 margin 作為間距
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "color": "#F9F2DC",
                        "action": {
                            "type": "message",
                            "label": "結束",
                            "text": "結束"  # 按下按鈕會發送此訊息
                        },
                        "flex": 1,
                        "margin": "md"  # 同樣設置 margin
                    }
                ]
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
        line_bot_api.reply_message(reply_token, TextSendMessage(text="目前沒有任何提醒訊息。請輸入新的提醒"))

def delete_warning_message(warning_message, reply_token):
    warn_collection.delete_one({'message': warning_message})
    remaining_warnings = list(warn_collection.find({}))
    show_warning_messages(reply_token)
    

def save_warning_message(message, reply_token):
    warn_collection.insert_one({"message": message})
    show_warning_messages(reply_token)
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
    