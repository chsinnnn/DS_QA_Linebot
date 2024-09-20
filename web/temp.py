
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import json
from bson.objectid import ObjectId

app = Flask(__name__)

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

# 提供主頁面 (index.html)
@app.route('/')
def index():
    return render_template('qqq.html')  # 確保 index.html 在 templates 資料夾中

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
        print("缺少單元名稱或題目 ID")
        return jsonify({"error": "單元名稱或題目 ID 缺失"}), 400
    
    if unit not in unit_collections:
        print(f"單元名稱不正確: {unit}")
        return jsonify({"error": "單元名稱不正確"}), 400
    
    collection = unit_collections[unit]
    try:
        result = collection.delete_one({"_id": ObjectId(question_id)})
        if result.deleted_count > 0:
            return jsonify({"message": "題目已成功刪除！"}), 200
        else:
            return jsonify({"error": "題目刪除失敗或題目不存在"}), 404
    except Exception as e:
        print(f"刪除題目時發生錯誤：{str(e)}")
        return jsonify({"error": f"刪除題目時發生錯誤：{str(e)}"}), 500

# 獲取單元列表
@app.route('/get_units', methods=['GET'])
def get_units():
    units = list(unit_collections.keys())
    return jsonify({"units": units})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
