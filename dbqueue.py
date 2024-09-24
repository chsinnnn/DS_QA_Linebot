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
            {"Question": "請說明雙重佇列如何模擬，並說明選擇佇列的策略是什麼。",
             "Answer": [
                "雙重佇列可以用兩個佇列來模擬，一個用來存儲從前端進入的元素，另一個用來存儲從後端進入的元素。選擇佇列策略時，要根據操作需求選擇合適的佇列，例如先入先出（FIFO）或後入先出（LIFO）。"
            ]},
            {"Question": "請說明多重佇列如何模擬，並說明選擇佇列的策略是什麼。",
             "Answer": [
                "雙重佇列可以用兩個佇列來模擬，一個用來存儲從前端進入的元素，另一個用來存儲從後端進入的元素。選擇佇列策略時，要根據操作需求選擇合適的佇列，例如先入先出（FIFO）或後入先出（LIFO）。"
            ]},
            {"Question": "請提出一種選擇佇列的策略，並說明如何運作。",
             "Answer": [
                "先進先出(FIFO)：先進入佇列的資料先被取出。",
                "後進先出(LIFO)：後進入佇列的資料先被取出。"
            ]},
            {"Question": "如何實現優先佇列(Priority Queue)？",
             "Answer": [
                "優先佇列是一種每個元素都有優先級的資料結構。可以使用堆(heap)來實現，確保每次取出的元素都是優先級最高的。"
            ]},
            {"Question": "比較佇列(Queue)和堆疊(Stack)的不同之處。",
             "Answer": [
                "佇列和堆疊都是資料結構，但佇列是先進先出（FIFO），而堆疊是先進後出（LIFO）。"
            ]},
            {"Question": "什麼是佇列？",
             "Answer": [
                "佇列是一種先進先出（FIFO）的資料結構，類似於排隊等候服務的概念。"
            ]},
            {"Question": "佇列的基本操作有哪些？",
             "Answer": [
                "佇列的基本操作包括入enqueue、dequeue、isEmpty等。"
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
