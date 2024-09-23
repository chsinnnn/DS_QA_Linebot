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
        collection = db.queue
        data = [
            {"Question": "如何計算單一佇列的平均等候時間(waiting time)？",
            "Answer": [
                "在單一佇列模擬中，計算平均等候時間是將每個客戶在佇列中等候的時間加總，再除以客戶總數。這樣能得到每位客戶的平均等候時間。"
            ]},
            {"Question": "如何計算單一佇列的平均佇列長度(queue length)？",
             "Answer": [
                "在單一佇列模擬中，平均佇列長度是計算所有時刻的佇列長度總和，然後除以總時間。這樣可以知道整體平均有多少個項目在佇列中。"
            ]},
            {"Question": "舉例說明雙重佇列如何模擬，須指出選擇佇列的策略。",
             "Answer": [
                "雙重佇列可以用兩個佇列來模擬，一個用來存儲從前端進入的元素，另一個用來存儲從後端進入的元素。選擇佇列策略時，要根據操作需求選擇合適的佇列，例如先入先出（FIFO）或後入先出（LIFO）。"
            ]},
            {"Question": "舉例說明多重佇列如何模擬，須指出選擇佇列的策略。",
             "Answer": [
                "雙重佇列可以用兩個佇列來模擬，一個用來存儲從前端進入的元素，另一個用來存儲從後端進入的元素。選擇佇列策略時，要根據操作需求選擇合適的佇列，例如先入先出（FIFO）或後入先出（LIFO）。"
            ]},
            {"Question": "提出二種選擇佇列的策略，並舉例比較二者。",
             "Answer": [
                "先進先出(FIFO)：先進入佇列的資料先被取出。",
                "後進先出(LIFO)：後進入佇列的資料先被取出。"
            ]}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
