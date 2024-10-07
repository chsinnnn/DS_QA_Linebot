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
import ast
import datetime
from linebot import AsyncLineBotApi
from linebot.models import FlexSendMessage, BubbleContainer, BoxComponent, TextComponent, ButtonComponent, SeparatorComponent, URIAction
os.chdir('/home/hsin/DS_QA_Linebot')
from chart_generator import generate_score_chart
from linebot.models import ImageSendMessage

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
mongo_collection = mongo_db["user_data"]
suggestion_collection = mongo_db["suggestions"]
warn_collection = mongo_db['WARN']

# 連Redis
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

special_student_ids = [ "11027104" ]

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
                    "text": "題目管理",
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

def handle_question_display(event, unit):  # 多個題目挑選
    collection = unit_collections[unit]

    questions = list(collection.find())
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
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"請回答以上你所選的問題\n(回答50字以下)"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="找不到題目"))

def handle_user_answer(event, user_answer, student_id):
    user_id = event.source.user_id

    if len(user_answer) > 50:
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
        answer_submitted_time = datetime.datetime.now().strftime("%Y-%m-%d")

        # 存儲用戶的答案
        redis_client.hset(user_id, "user_answer", user_answer)

        # 從 Redis 中讀取學號
        student_id = redis_client.hget(user_id, "student_id")

        if student_id:
            # 確保題目和答案的鍵存在於 Redis 中
            qa_key = f"{student_id}_qa:{question_title}"
            answer_time_key = f"{student_id}_answer_time:{question_title}"
            score_key = f"{student_id}_score:{question_title}"

            # 將用戶的答案存儲在列表中
            redis_client.rpush(qa_key, user_answer)
            redis_client.rpush(answer_time_key, answer_submitted_time)

        else:
            # 如果無法找到學號，則拋出錯誤或採取其他適當的處理方式
            print("無法找到學號，無法存儲題目和用戶答案")

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
                answers = result.get("Answer", ["未找到答案"])
                formatted_answers = ',\n'.join([f'"{answer}"' for answer in answers])
                
                found = True
                break  # 找到後跳出迴圈，或繼續尋找其他 collection 中的可能結果

        if not found:
            print("未在任何 collection 中找到對應的題目。")

        print(formatted_answers)
        #reply = f'"題目"："{question_title}",\n"回答"："{user_answer}",\n{reference_answers}'
        reply = f'"question"："{question_title}",\n"student_answer"："{user_answer}",\n"reference_answer": [\n{formatted_answers}\n]'
        print(reply)
        # 將題目發送給 語言模型並回傳答案
        answer = send_question_to_mymodel(reply)
        print(answer)

        # 組合要回覆的文字訊息，包括用戶的回答和 語言模型評論
        #reply_text = f"題目：{question_title}\n\n您回答：{user_answer}\n\n評論：{answer}"
        #reply_text = f"{answer}"
        # 定義生成星星圖案的函數
        def generate_star_rating(score):
            # 確保 score 是整數
            try:
                score = int(score)  # 將 score 轉換為整數
            except ValueError:
                score = 0  # 如果轉換失敗，設置為 0（或其他預設值）
            
            # 根據分數生成星星
            return "★" * score + "☆" * (3 - score)  # 3 為滿分
        # 根據評分生成星星圖案
        star_rating = generate_star_rating(answer['評分'])

        # 組合要回覆的文字訊息，包括用戶的回答和語言模型評論
        reply_text = f"評分: {star_rating} ({answer['評分']})\n評論: {answer['評論']}"
            
        # 使用 TextSendMessage 回覆文字訊息
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

        # 儲存評分結果
        redis_client.rpush(score_key, answer['評分'])

        # 清除當前題目和用戶回答
        redis_client.hdel(user_id, "current_question")
        redis_client.hdel(user_id, "user_answer")
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="未找到對應的問題，請重新選擇題目。"))

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
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="謝謝您的回饋 ! "))
                #本來是連不上模型伺服器的話，就回覆謝謝您的回饋
             # 發送意見到電子郵件
            try:
                subject = f"來自學生 {student_id} 的意見回饋"
                body = f"學號: {student_id}\n意見回饋: {suggestion}"
                yag.send(to='linechattt@gmail.com', subject=subject, contents=body)
                print("Suggestion email sent successfully!")
            except Exception as e:
                print(f"Failed to send email: {e}")
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
                "text": f"總回答題數:{details['count']}",
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
    pattern = f"{student_id}_answer_time:*"
    answer_time_keys = redis_client.keys(pattern)
    question_titles = [key.split(':')[1] for key in redis_client.keys(pattern)]

    if not answer_time_keys:
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

    for key in answer_time_keys:
        answer_times = redis_client.lrange(key, 0, -1)
        question_title = key.split("_answer_time:")[1]

        # 如果問題已經計算過，跳過
        if question_title in calculated_questions:
            continue

        for unit, collection in unit_collections.items():
            if collection.find_one({"Question": question_title}):
                unit_name = unit
                if unit_name not in unit_answer_counts:
                    unit_answer_counts[unit_name] = {"count": 0, "times": {}}
                unit_answer_counts[unit_name]["count"] += 1  # 每個問題只計算一次
                for time in answer_times:
                    if time not in unit_answer_counts[unit_name]["times"]:
                        unit_answer_counts[unit_name]["times"][time] = 0
                    unit_answer_counts[unit_name]["times"][time] += 1
                # 標記問題為已計算
                calculated_questions.add(question_title)
                break

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
    score_distribution = {1: 0, 2: 0, 3: 0}
    
    # 建立 Redis 鍵模式
    pattern = f"{student_id}_score:*"
    
    # 獲取所有符合模式的鍵
    score_keys = redis_client.keys(pattern)
    for key in score_keys:
        score = redis_client.lrange(key, 0, -1)
        question_title = key.split("_score:")[1]

        for unit, collection in unit_collections.items():
            if unit == unit_name and collection.find_one({"Question": question_title}):
                for s in score:
                    score_distribution[int(s)] += 1

    # 返回分數分佈
    return score_distribution
        
def send_question_to_mymodel(question):
    # 設定語言模型API的URL
    model_api_url = "http://192.168.100.140:5001/generate"  # 替換為語言模型伺服器的IP地址和端口號

    # 準備發送的數據
    payload = {
        "input_text": question  # 修改這裡的鍵名為 input_text，符合API預期的字段
    }

    try:
        # 發送POST請求到語言模型的API
        response = requests.post(model_api_url, json=payload)
        # 檢查請求是否成功
        if response.status_code == 200:
            # 解析回覆的JSON數據
            data = response.json()
            score = data.get("score", "未提供評分")
            comment = data.get("comment", "未提供評論")
            
            # 返回結果作為字典
            return {"評分": score, "評論": comment}
        elif response.status_code == 500:
            print("模型格式錯誤")
            return "模型格式錯誤"
        else:
            print(f"Error: Received status code {response.status_code}")
            return "模型回覆失敗，請稍後再試。"
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return "無法連接到模型伺服器。"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    user_id = event.source.user_id
    user_profile = line_bot_api.get_profile(user_id)
    user_name = user_profile.display_name
    user_document = mongo_collection.find_one({"user_id": user_id})
    student_id = None if user_document is None else user_document.get("student_id")
    msg = event.message.text
    awaiting_suggestion = redis_client.hget(user_id, 'awaiting_suggestion')


    if awaiting_suggestion:
        handle_suggestion(event, student_id)
    elif redis_client.hexists(user_id, 'student_id') and mongo_collection.find_one({"user_id": user_id}):
        if msg == "我要作答" and student_id not in special_student_ids :  #學生
            handle_unit_selection(event)
        elif msg == "我要作答" and student_id in special_student_ids :  #老師助教
            handle_question_insert(event)
        elif msg == "歡迎留下您寶貴的建議:D":
            if student_id in special_student_ids:
                handle_admin_view_suggestions(event)
            else:
                redis_client.hset(user_id, 'awaiting_suggestion', 'true')
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入您的建議。"))
        elif msg in unit_collections:  #學生
            handle_question_display(event, msg)
        elif msg.startswith("我要回答:"):
            question_title = msg[6:]
            handle_question_answer(event, question_title)
        elif redis_client.hget(user_id, "current_question"):
            handle_user_answer(event, msg, student_id)
        elif msg == "顯示作答紀錄":
            show_unit_answer_records(event, student_id)
        elif msg.startswith('查看') and msg.endswith('分數分布'):
            unit_name = msg[2:-5]
            score_distribution = calculate_score_distribution(unit_name, student_id)
            score_distribution_str = str(score_distribution)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=score_distribution_str))

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
    
    else:
        if is_valid_student_id(msg):
            reply = handle_student_id(user_id, user_name, msg)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請先輸入符合格式的學號（8位數字）。"))


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
    