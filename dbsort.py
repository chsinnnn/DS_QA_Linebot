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
            {"Question": "撰寫程式碼說明氣泡排序bubble sort如何提早結束執行。"},
            {"Question": "舉例解說選擇排序selection sort並非穩定stable的排序方法。"},
            {"Question": "撰寫程式碼指出影響氣泡排序是否穩定stable的關鍵指令。"},
            {"Question": "撰寫程式碼指出影響插入排序insertion sort是否穩定stable的關鍵指令。"},
            {"Question": "依據程式碼解說選擇排序的時間複雜度。"},
            {"Question": "舉例比較氣泡排序和選擇排序的資料交換swap次數，何者較多？"},
            {"Question": "舉例說明何時插入排序的資料搬動次數比希爾排序shell sort多？"},
            {"Question": "舉例說明何時希爾排序的資料搬動次數比插入排序多？"},
            {"Question": "舉例說明合併排序的遞迴深度和資料筆數的關係。"},
            {"Question": "舉例說明快速排序的遞迴深度會受何者影響。"},
            {"Question": "舉例解說希爾排序shell sort是否穩定stable。"},
            {"Question": "舉例解說快速排序quick sort是否穩定stable。"},
            {"Question": "為快速排序提出選擇基準pivot的方法，並舉例說明優點。"}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
    
