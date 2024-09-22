from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from pymongo import MongoClient
import json
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用於 session 加密

# 連接 MongoDB 資料庫
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["testdb"]

unit_collections = {
    "其他": mongo_db["other"],
    "指標": mongo_db["pointer"],
    "佇列": mongo_db["queue"],
    "遞迴": mongo_db["recursion"],
    "排序": mongo_db["sort"],
    "堆疊": mongo_db["stack"],
    "二元樹": mongo_db["bst"]
}

# 模擬的使用者資料
users = {
    "teacher": "teacher",  # 帳號: 密碼
    "11027149": "chsinn18",
    "11027104": "11027104",
    "11027138": "11027384"
}

# 提供主頁面 (index.html)
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    return render_template('qqq.html')  # 確保 qqq.html 在 templates 資料夾中

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

    if username in users and users[username] == password:
        session['username'] = username
        return jsonify({"message": "登入成功！"}), 200
    else:
        return jsonify({"error": "帳號或密碼不正確"}), 401

# 確認使用者是否登入
@app.route('/check_login')
def check_login():
    if 'username' in session:
        return jsonify({"logged_in": True, "username": session['username']}), 200
    else:
        return jsonify({"logged_in": False}), 200

@app.route('/logout', methods=['POST'])
def logout():
  # 添加這行來檢查是否收到請求
    session.pop('username', None)  # 清除 session 中的 username
    return jsonify({"message": "已成功登出"}), 200

# API 端點，處理前端的題目、答案與單元名稱
@app.route('/add_question', methods=['POST'])
def add_question():
    data = request.get_json()
    unit = data.get('unit')
    question = data.get('question')
    answer = data.get('answer')
    
    if not unit or not question or not answer:
        return jsonify({"error": "單元名稱、題目和答案是必填的"}), 400

    collection = unit_collections.get(unit)
    if not collection:
        return jsonify({"error": "單元名稱不正確"}), 400
    
    formatted_answer = json.dumps([answer], ensure_ascii=False)
    collection.insert_one({"Question": question, "Answer": formatted_answer})
    
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
