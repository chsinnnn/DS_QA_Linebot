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

# Line Bot閮剖��
with open('config.json') as config_file:
    config = json.load(config_file)

access_token = config['LINE_ACCESS_TOKEN']
secret = config['LINE_SECRET']

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(secret)

# ��ΚongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["testdb"]
mongo_collection = mongo_db["user_data"]
suggestion_collection = mongo_db["suggestions"]
warn_collection = mongo_db['WARN']

# ��Οedis
redis_host = 'localhost'
redis_port = 6379
redis_db = 0
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

special_student_ids = [ '11027149','11027104', '11027133' ]

# MongoDB閮剖��
unit_collections = {
    "��嗡��": mongo_db["other"],
    "���璅�": mongo_db["pointer"],
    "雿����": mongo_db["queue"],
    "���餈�": mongo_db["recursion"],
    "���摨�": mongo_db["sort"],
    "������": mongo_db["stack"]
}

def is_valid_student_id(student_id):
    return student_id.isdigit() and len(student_id) == 8

def handle_student_id(user_id, user_name, msg):
    if is_valid_student_id(msg):
        # 摮貉����澆��甇�蝣綽��瑼Ｘ�亙飛�����臬�血歇蝬�摮���冽�� MongoDB 銝�
        db_existing = mongo_collection.find_one({"user_id": user_id})
        red_existing = redis_client.hexists(user_id, 'student_id')
        if db_existing and red_existing:
            reply = f"{user_name}嚗���函��摮貉��撌脩����駁�����鈭����"
        else:
            # 撠�摮貉��摮���� Redis 銝�
            redis_client.hset(user_id, 'student_id', msg)
            # ������撠�摮貉��摮���� MongoDB 銝�
            student_data = {"user_id": user_id, "name": user_name, "student_id": msg}
            mongo_collection.insert_one(student_data)
            reply = f"{user_name}嚗�摮貉��撌脩�����������嚗�隢�暺���貉”��桃�����閬�雿�蝑�銝阡�賊�����!!"
    else:
        reply = "摮貉����澆��銝�甇�蝣綽��隢�頛詨��8雿���詨�����摮貉�����"
    return reply

def handle_unit_selection(event):
    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label="��嗡��", text="��嗡��")),
        QuickReplyButton(action=MessageAction(label="���璅�", text="���璅�")),
        QuickReplyButton(action=MessageAction(label="雿����", text="雿����")),
        QuickReplyButton(action=MessageAction(label="���餈�", text="���餈�")),
        QuickReplyButton(action=MessageAction(label="���摨�", text="���摨�")),
        QuickReplyButton(action=MessageAction(label="������", text="������"))
    ])

    message = TextSendMessage(text="隢���豢��銝������桀��", quick_reply=quick_reply)
    line_bot_api.reply_message(event.reply_token, message)

def handle_question_display(event, unit):  # 憭����憿���格�����
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
                        "text": "憿����",
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
                            "label": f"���蝑�",
                            "text": f"���蝑�{question['Question']}"
                        }
                    }
                ]
            },
            "styles": {
                "header": {
                    "backgroundColor": "#668166"  # header摨����
                }
            }
        }
        bubbles.append(bubble)

    flex_message = FlexSendMessage(
        alt_text="��豢��憿����",
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

def handle_question_answer(event, question_title):  # 撌脤�詨末憿����
    question = None
    for unit, collection in unit_collections.items():
        question = collection.find_one({"Question": question_title})
        if question:
            break

    if question:
        user_id = event.source.user_id
        redis_client.hset(user_id, "current_question", question_title)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"隢����蝑�隞乩�����憿�嚗�\n\n{question_title}"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="��曆����圈�����"))

def handle_user_answer(event, user_answer):
    user_id = event.source.user_id
    question_title = redis_client.hget(user_id, "current_question")

    if question_title:
        # 蝝�������蝑�憿���桃��������
        answer_submitted_time = datetime.datetime.now().strftime("%Y-%m-%d")

        # 摮���脩�冽�嗥��蝑�獢�
        redis_client.hset(user_id, "user_answer", user_answer)

        # 敺� Redis 銝剛�����摮貉��
        student_id = redis_client.hget(user_id, "student_id")

        if student_id:
            # 蝣箔��憿���桀��蝑�獢������萄����冽�� Redis 銝�
            qa_key = f"{student_id}_qa:{question_title}"
            answer_time_key = f"{student_id}_answer_time:{question_title}"

            # 撠���冽�嗥��蝑�獢�摮���脣�典��銵其葉
            redis_client.rpush(qa_key, user_answer)
            redis_client.rpush(answer_time_key, answer_submitted_time)

        else:
            # 憒������⊥����曉�啣飛���嚗���������粹�航炊�����∪����嗡����拍�嗥����������孵��
            print("��⊥����曉�啣飛���嚗���⊥��摮���脤����桀����冽�嗥��獢�")

        # 撠�憿���桃�潮��蝯� Llama3 隡箸����其蒂�����喟��獢�
        llama3_answer = send_question_to_llama3(question_title)

        # 蝯����閬����閬�������摮�閮���荔�������祉�冽�嗥�����蝑���� Llama3 ������蝑�
        reply_text = f"憿���殷��{question_title}\n\n��典��蝑�嚗�{user_answer}\n\nLlama3 ���蝑�嚗�{llama3_answer}"

        # 雿輻�� TextSendMessage ���閬����摮�閮����
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

        # 皜���斤�嗅��憿���桀����冽�嗅��蝑�
        redis_client.hdel(user_id, "current_question")
        redis_client.hdel(user_id, "user_answer")
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="��芣�曉�啣�����������憿�嚗�隢������圈�豢��憿���柴��"))

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
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="雓�雓���函��撱箄降嚗������������芸����寥�脯��"))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="隢�頛詨�交�函��撱箄降���"))

def send_quick_ans_records_reply(reply_token):
    quick_reply = QuickReply(
        items=[
        QuickReplyButton(action=MessageAction(label="��券��", text="��亦�������券�具�����雿�蝑�蝝����")),
        QuickReplyButton(action=MessageAction(label="��嗡��", text="��亦����桀�������嗡��������雿�蝑�蝝����")),
        QuickReplyButton(action=MessageAction(label="���璅�", text="��亦����桀��������璅�������雿�蝑�蝝����")),
        QuickReplyButton(action=MessageAction(label="雿����", text="��亦����桀�����雿����������雿�蝑�蝝����")),
        QuickReplyButton(action=MessageAction(label="���餈�", text="��亦����桀��������餈氬�����雿�蝑�蝝����")),
        QuickReplyButton(action=MessageAction(label="���摨�", text="��亦����桀��������摨�������雿�蝑�蝝����")),
        QuickReplyButton(action=MessageAction(label="������", text="��亦����桀�����������������雿�蝑�蝝����"))
        ]
    )
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text="��豢��閬���亦��雿�蝑�蝝���������桀��", quick_reply=quick_reply)
    )

def show_unit_answer_records(event, student_id, selected_unit):
    # 雿輻�� keys ��賣�貊�脣�����������閰� student_id ��賊�����蝑�憿���������� keys
    pattern = f"{student_id}_answer_time:*"
    answer_time_keys = redis_client.keys(pattern)
    question_titles = [key.split(':')[1] for key in redis_client.keys(pattern)]

    # 瑼Ｘ�交�臬�衣�脣����� keys
    if not answer_time_keys:
        line_bot_api.reply_message(event.reply_token, "瘝������曉�唬遙雿�蝑�憿�閮�������")
    else:
    # ���甇� keys嚗���脣��銝行�澆�����蝑�憿�������
        unit_answer_counts = {}
        for key in answer_time_keys:
            answer_times = redis_client.lrange(key, 0, -1)
            question_title = key.split("_answer_time:")[1]

            # ��湔�乩蝙��� question_title_key ��亥岷嚗���踹��銝�敹�閬������批惜敺芰��
            for unit, collection in unit_collections.items():
                if collection.find_one({"Question": question_title}):
                    unit_name = unit
                    if unit_name not in unit_answer_counts:
                        unit_answer_counts[unit_name] = {"count": 0, "times": {}}
                    unit_answer_counts[unit_name]["count"] += len(answer_times)  # ��湔�亙��������蝑�甈⊥��
                    for time in answer_times:
                        if time not in unit_answer_counts[unit_name]["times"]:
                            unit_answer_counts[unit_name]["times"][time] = 0
                        unit_answer_counts[unit_name]["times"][time] += 1
                    break  # ��曉�啣�������桀��敺�頝喳�箏儐���

        if selected_unit in unit_answer_counts:
            details = unit_answer_counts[selected_unit]
            units_reply_message = (
                f"��桀��: {selected_unit} ���蝑�甈⊥��: {details['count']} \n蝑�憿����������憿����:\n" +
                "".join([f"{time}: {count}憿�\n" if i < len(list(details['times'].items())) - 1 else f"{time}: {count}憿�" for i, (time, count) in enumerate(list(details['times'].items()))])
            )
        elif selected_unit == "��券��":
            all_units_reply_message = ""
            for unit, details in unit_answer_counts.items():
                times_and_num = "".join([f"{time}: {count}憿�\n" if i < len(list(details['times'].items())) - 1 else f"{time}: {count}憿�" for i, (time, count) in enumerate(list(details['times'].items()))])
                # 瘙箏����臬�血�冽�啁����桀��靽⊥�臬��瘛餃�����銵�蝚�
                if all_units_reply_message == "":  # 憒����銝���舐洵銝������桀��嚗�瘛餃�����銵�蝚�
                    unit_message = f"��桀��: {unit} ���蝑�甈⊥��: {details['count']} \n蝑�憿����������憿����:\n{times_and_num}"
                else:  # 憒������舐洵銝������桀��嚗�銝���券����剖�����銵�蝚�
                    unit_message = f"\n\n��桀��: {unit} ���蝑�甈⊥��: {details['count']} \n蝑�憿����������憿����:\n{times_and_num}"
                
                all_units_reply_message += unit_message

            units_reply_message = all_units_reply_message
        else:
            units_reply_message = f"��桀��: {selected_unit}\n瘝������曉�唬遙雿�蝑�憿�閮�������"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=units_reply_message))

def send_question_to_llama3(question):
    llama3_server_url = 'http://192.168.100.137:5000/ask'

    try:
        print(f"Sending question to Llama3 server: {llama3_server_url}")
        response = requests.post(llama3_server_url, json={'question': question})
        response.raise_for_status()
        answer = response.json().get('answer', '��⊥����脣�����蝑�')
        print(f"Received answer from Llama3 server: {answer}")
        return answer
    except requests.exceptions.RequestException as e:
        print(f"Error sending question to Llama3: {e}")
        return '��⊥����脣�����蝑�'

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
        if msg == "���閬�雿�蝑�":
            handle_unit_selection(event)
        elif msg == "甇∟�����銝���典窄鞎渡��撱箄降:D":
            redis_client.hset(user_id, 'awaiting_suggestion', 'true')
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="隢�頛詨�交�函��撱箄降���"))
        elif msg in unit_collections:
            handle_question_display(event, msg)
        elif msg.startswith("���蝑�"):
            question_title = msg[2:]
            handle_question_answer(event, question_title)
        elif redis_client.hget(user_id, "current_question"):
            handle_user_answer(event, msg)
        elif msg == "憿舐內雿�蝑�蝝����":
            send_quick_ans_records_reply(event.reply_token)
        elif msg.startswith("��亦��") and msg.endswith("���雿�蝑�蝝����"):
            # 敺�瘨���舀����砌葉��������桀�����蝔�
            selected_unit = msg.split("���")[1].split("���")[0]
            # 隤輻�典�賣�賊＊蝷箄府��桀�����雿�蝑�蝝����
            show_unit_answer_records(event, student_id, selected_unit)
        elif student_id in special_student_ids:
            if msg == "撠�������":
                send_quick_reply(event.reply_token)
                # 閮剔蔭璅�隤�隞亥”蝷箇�冽�嗥�曉�典�臭誑頛詨�交�����閮����
                redis_client.hset(user_id, 'awaiting_warning_message', 'true')
            elif msg.startswith("��芷�斗�����"):
                show_warning_messages(event.reply_token)
            elif msg.startswith("��亦��������"):
                send_warning_message(event.reply_token)
                redis_client.hdel(user_id, 'awaiting_warning_message')  
            elif msg.startswith("��芷��:"):
                warning_message = msg.split(':')[1]
                delete_warning_message(warning_message, event.reply_token)
            elif msg == "靽����������������":
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="隢�頛詨�交�啁��������"))
                # �����啗身蝵格��隤�隞亥”蝷箇�冽�嗥�曉�典�臭誑頛詨�交�����閮����
                redis_client.hset(user_id, 'awaiting_warning_message', 'true')
            else:
                # ��典�脣��������閮���臭�����瑼Ｘ�交�臬�衣�������函��敺�������閮���舐��頛詨��
                if redis_client.hget(user_id, 'awaiting_warning_message') == 'true':
                    save_warning_message(msg, event.reply_token)
                    # 皜���斗��隤�
                    redis_client.hdel(user_id, 'awaiting_warning_message')
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="��⊥�����隞歹��隢������啗撓��乓��"))
        elif student_id not in special_student_ids and msg == "撠�������":
            send_warning_message(event.reply_token)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="��⊥�����隞歹��隢������啗撓��乓��"))
    
    else:
        if is_valid_student_id(msg):
            reply = handle_student_id(user_id, user_name, msg)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="隢����頛詨�亦泵�����澆�����摮貉��嚗�8雿���詨��嚗����"))

def send_quick_reply(reply_token):
    quick_reply_buttons = QuickReply(
        items=[
            QuickReplyButton(action=MessageAction(label="���", text="��芷�斗�����")),
            QuickReplyButton(action=MessageAction(label="���", text="靽����������������")),
            QuickReplyButton(action=MessageAction(label="��亦��������", text="��亦��������"))
        ]
    )
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text="閬���芷�文����������������������交�啁�����������嚗�", quick_reply=quick_reply_buttons)
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
                            "text": f"��芷��:{warning['message']}"
                        },
                    }
                ]
            })
            # ���������
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
                        "text": "撠�������",
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
                    "backgroundColor": "#668166" #header摨����
                }
            }
        }

        flex_message = FlexSendMessage(
            alt_text="撠�������",
            contents=bubble
        )
        line_bot_api.reply_message(reply_token, flex_message)
    else:
        # 憒����瘝������������臭誑��芷�歹�����蝷箇�冽�嗉撓��交�啁��������
        line_bot_api.reply_message(reply_token, TextSendMessage(text="��桀��瘝����隞颱��������閮���胯��隢�頛詨�交�啁��������"))

def delete_warning_message(warning_message, reply_token):
    warn_collection.delete_one({'message': warning_message})
    remaining_warnings = list(warn_collection.find({}))
    if remaining_warnings:
        quick_reply_buttons = QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="���", text="��芷�斗�����")),
                QuickReplyButton(action=MessageAction(label="���", text="靽����������������")),
                QuickReplyButton(action=MessageAction(label="��亦��������", text="��亦��������"))
            ]
        )
        line_bot_api.reply_message(reply_token, TextSendMessage(text="������撌脣�芷�扎����券��閬���芷�文�嗡�����������嚗�憒����銝���芷�歹��隢�頛詨�交�啁��������", quick_reply=quick_reply_buttons))
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="������撌脣�芷�扎��隢�頛詨�交�啁�����������"))

def save_warning_message(message, reply_token):
    warn_collection.insert_one({"message": message})
    send_warning_message(reply_token)
    ##line_bot_api.reply_message(reply_token, TextSendMessage(text="������閮���臬歇��脣�����"))

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
            # ���������
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
                        "text": "撠�������",
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
                    "backgroundColor": "#668166" #header摨����
                }
            }
        }

        flex_message = FlexSendMessage(
            alt_text="撠�������",
            contents=bubble
        )
        line_bot_api.reply_message(reply_token, flex_message)
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="��桀��瘝����隞颱��������閮���胯��"))

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
