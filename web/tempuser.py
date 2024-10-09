from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from pymongo import MongoClient
import json
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用於 session 加密

# 連接 MongoDB 資料庫
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["testdb"]
collections = mongo_db["users"]

unit_collections = {
    "其他": mongo_db["other"],
    "指標": mongo_db["pointer"],
    "佇列": mongo_db["queue"],
    "遞迴": mongo_db["recursion"],
    "排序": mongo_db["sort"],
    "堆疊": mongo_db["stack"],
    "二元樹": mongo_db["bst"]
}

'''
username = "teacher"
password = "teacher"
role = "superuser"
# 對密碼進行哈希處理
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# 將新使用者插入資料庫
new_user = {
    "username": username,
    "password": hashed_password,  # 儲存加密後的密碼
    "role": role
}
collections.insert_one(new_user)
'''

# 提供主頁面 (index.html)
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('homepage.html')  # 改為新的首頁模板


# 登入頁面
@app.route('/login')
def login_page():
    return render_template('login.html')  # 登入頁面模板

# 處理登入請求
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "帳號和密碼是必填的"}), 400

    # 從資料庫中查找使用者
    user = collections.find_one({"username": username})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):  # 驗證密碼
        session['username'] = username
        session['role'] = user['role']  # 儲存角色資訊到 session
        return jsonify({"message": "登入成功！"}), 200
    else:
        return jsonify({"error": "帳號或密碼不正確"}), 401


# 確認使用者是否登入
@app.route('/check_login')
def check_login():
    if 'username' in session:
        return jsonify({"logged_in": True, "username": session['username'], "role": session['role']}), 200
    else:
        return jsonify({"logged_in": False}), 200

# 增加管理使用者的頁面
@app.route('/manage_users')
def manage_users():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    if session['role'] != 'superuser':
        return jsonify({"error": "你沒有權限訪問此頁面"}), 403

    return render_template('user.html')  # 渲染 user.html 頁面


# 新增使用者
@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        print("Received data:", data)  # 檢查伺服器是否接收到資料
        username = data['username']
        password = data['password']
        role = data['role']

        # 檢查使用者是否已經存在
        existing_user = collections.find_one({"username": username})
        if existing_user:
            return jsonify({"error": "User already exists"}), 400

        # 對密碼進行哈希處理
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # 將新使用者插入資料庫
        new_user = {
            "username": username,
            "password": hashed_password,  # 儲存加密後的密碼
            "role": role
        }
        collections.insert_one(new_user)

        return jsonify({"message": "新增使用者成功!"}), 201
    except Exception as e:
        print("Error adding user:", e)
        return jsonify({"error": "新增使用者失敗!"}), 500

# 刪除使用者
@app.route('/get_users', methods=['GET'])
def get_users():
    if 'username' not in session or session['role'] != 'superuser':
        return jsonify({"error": "你沒有權限執行此操作"}), 403

    users_list = list(collections.find({}, {"_id": 1, "username": 1}))  # 獲取所有使用者資料
    for user in users_list:
        user['_id'] = str(user['_id'])  # 將 ObjectId 轉成字串

    return jsonify({"users": users_list}), 200


@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    if 'username' not in session or session['role'] != 'superuser':
        return jsonify({"error": "你沒有權限執行此操作"}), 403
        
    user_id = request.args.get('id')  # 只檢查 user_id

    if not user_id:
        return jsonify({"error": "ID 缺失"}), 400

    try:
        result = collections.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "使用者已成功刪除！"}), 200
        else:
            return jsonify({"error": "使用者刪除失敗或使用者不存在"}), 404
    except Exception as e:
        return jsonify({"error": f"刪除使用者時發生錯誤：{str(e)}"}), 500

    


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  # 清除 session 中的 username
    session.pop('role', None)  # 清除 session 中的 role
    return jsonify({"message": "已成功登出"}), 200

@app.route('/manage_question')
def manage_question():
    return render_template('topic.html')  # 渲染 topic.html 頁面

# API 端點，處理前端的題目、答案與單元名稱
@app.route('/add_question', methods=['POST'])
def add_question():
    data = request.get_json()
    unit = data.get('unit')
    question = data.get('question')
    answer = data.get('answer')
    type = data.get('type')
    if not unit or not question or not answer:
        return jsonify({"error": "單元名稱、題目和答案是必填的"}), 400

    collection = unit_collections.get(unit)
    if not collection:
        return jsonify({"error": "單元名稱不正確"}), 400

    formatted_answer = json.dumps([answer], ensure_ascii=False)
    collection.insert_one({"Question": question, "Answer": formatted_answer, "Type": type})

    return jsonify({"message": "題目已成功新增！"}), 200

# 獲取題目列表
@app.route('/get_questions', methods=['GET'])
def get_questions():
    unit = request.args.get('unit')
    if unit not in unit_collections:
        return jsonify({"error": "單元名稱不正確"}), 400

    collection = unit_collections[unit]
    questions = list(collection.find({}, {"_id": 1, "Question": 1}))

    for question in questions:
        question['_id'] = str(question['_id'])

    return jsonify({"questions": questions})

# 刪除題目
@app.route('/delete_question', methods=['DELETE'])
def delete_question():
    unit = request.args.get('unit')
    question_id = request.args.get('id')

    if not unit or not question_id:
        return jsonify({"error": "單元名稱或題目 ID 缺失"}), 400

    if unit not in unit_collections:
        return jsonify({"error": "單元名稱不正確"}), 400

    collection = unit_collections[unit]
    try:
        result = collection.delete_one({"_id": ObjectId(question_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "題目已成功刪除！"}), 200
        else:
            return jsonify({"error": "題目刪除失敗或題目不存在"}), 404
    except Exception as e:
        return jsonify({"error": f"刪除題目時發生錯誤：{str(e)}"}), 500


# 獲取單元列表
@app.route('/get_units', methods=['GET'])
def get_units():
    units = list(unit_collections.keys())
    return jsonify({"units": units})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
