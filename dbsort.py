from pymongo import MongoClient
from pprint import pprint

def connect_to_database():
    try:
        client = MongoClient("mongodb://localhost:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5")
        db = client.testdb
        print("Connected to MongoDB")
        return db
    except Exception as error:
        print("Failed to connect to MongoDB:", error)
        return None

def create_new_data(db):
    try:
        collection = db.sort
        data = [
            {"Question": "撰寫程式碼說明氣泡排序bubble sort如何提早結束執行。", "Answer": "xx"},
            {"Question": "舉例解說選擇排序selection sort並非穩定stable的排序方法。", "Answer": "xx"},
            {"Question": "撰寫程式碼指出影響氣泡排序是否穩定stable的關鍵指令。", "Answer": "xx"},
            {"Question": "撰寫程式碼指出影響插入排序insertion sort是否穩定stable的關鍵指令。", "Answer": "xx"},
            {"Question": "依據程式碼解說選擇排序的時間複雜度。", "Answer": "xx"},
            {"Question": "舉例比較氣泡排序和選擇排序的資料交換swap次數，何者較多？", "Answer": "xx"},
            {"Question": "舉例說明何時插入排序的資料搬動次數比希爾排序shell sort多？", "Answer": "xx"},
            {"Question": "舉例說明何時希爾排序的資料搬動次數比插入排序多？", "Answer": "xx"}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
