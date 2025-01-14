from pymongo import MongoClient
from bson.objectid import ObjectId

# 連接到 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["testdb"]
collection = db["user_data"]

# 指定要刪除的記錄的 ObjectId
record_id = ObjectId('665768e0c0cf56a42b4ade08')

# 指定要刪除的記錄的條件
query = {
    "_id": record_id,
    "user_id": "U32d626ea668e67a3a5a3e8d0c079508a",
    "name": "游婕歆",
    "student_id": "11027149"
}

# 刪除匹配條件的第一條記錄
result = collection.delete_one(query)

if result.deleted_count == 1:
    print("記錄成功刪除")
else:
    print("找不到匹配的記錄")

# 關閉連接
client.close()
