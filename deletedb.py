from pymongo import MongoClient

# 連接到 MongoDB
client = MongoClient("mongodb://localhost:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5")

# 指定資料庫名稱
db_name = 'teststudentdata'
db = client[db_name]

# 指定要刪除的 collection 名稱
collection_name = 'secondclass'

# 刪除 collection
try:
    db[collection_name].drop()
    print(f"Collection '{collection_name}' 刪除成功")
except Exception as e:
    print(f"刪除 collection 時發生錯誤: {e}")
