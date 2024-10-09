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
            {'Question': '如何計算單一佇列的平均等候時間(waiting time)？',
            'Answer': ['單一佇列的平均等候時間計算方式是：將每個任務的等候時間加總，再除以任務總數。公式：平均等候時間 = (總等候時間) / (任務數量)。'],
            'Type': '開放式問題'},
            {'Question': '請說明雙重佇列如何模擬，並說明選擇佇列的策略是什麼。',
            'Answer': ['雙重佇列（Deque）可用雙端操作的結構來模擬，允許從兩端插入和刪除元素。選擇策略依需求而定，如需高效雙端操作則選用Deque。'],
            'Type': '開放式問題'},
            {'Question': '請提出一種選擇佇列的策略，並說明如何運作。',
            'Answer': ['可以使用"優先佇列"策略，依據元素優先級處理資料。運作方式是優先處理高優先級的元素，確保重要任務比低優先級的先被執行。'],
            'Type': '開放式問題'},
            {'Question': '比較佇列(Queue)和堆疊(Stack)的不同之處。',
            'Answer': ['佇列是先進先出(FIFO)，元素從尾部加入，從頭部移出；堆疊是先進後出(LIFO)，元素從頂部加入並移出。'],
            'Type': '開放式問題'},
            {'Question': '如何實現優先佇列(Priority Queue)？',
            'Answer': ['優先佇列可用二元堆（如最大堆或最小堆）實現，確保每次都能快速取出具有最高或最低優先級的元素。'],
            'Type': '開放式問題'},
            {'Question': '什麼是佇列(Queue)？',
            'Answer': ['佇列（Queue）是一種先進先出（FIFO）的資料結構，類似排隊。元素從佇列尾端加入，從佇列前端移出。'],
            'Type': '開放式問題'},
            {'Question': '佇列(Queue)的基本操作有哪些？',
            'Answer': ['佇列的基本操作有：enqueue將元素加入佇列尾端，dequeue移除前端元素，查看佇列前端元素（front/peek），以及檢查佇列是否為空（isEmpty）。'],
            'Type': '開放式問題'},
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
