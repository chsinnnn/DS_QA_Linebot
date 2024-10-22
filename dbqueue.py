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
                "單一佇列的平均等候時間計算方式是：將每個任務的等候時間加總，再除以任務總數。公式：平均等候時間 = (總等候時間) / (任務數量)。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "請說明雙重佇列如何模擬，並說明選擇佇列的策略是什麼。",
             "Answer": [
                "雙重佇列模擬可用兩個獨立佇列處理不同優先級的任務。選擇策略常依優先級決定，優先處理高優先級佇列的任務。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "請提出一種選擇佇列的策略，並說明如何運作。",
             "Answer": [
                "可以使用優先佇列策略，依據元素優先級處理資料。運作方式是優先處理高優先級的元素，確保重要任務比低優先級的先被執行。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "比較佇列(Queue)和堆疊(Stack)的不同之處。",
             "Answer": [
                "佇列是先進先出（FIFO），最先加入的元素最先移除；堆疊是後進先出（LIFO），最後加入的元素最先移除。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "如何實現優先佇列(Priority Queue)？",
             "Answer": [
                "優先佇列可用heap實現，元素根據優先級插入，較高優先級的元素會先被取出。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "什麼是佇列(Queue)？",
             "Answer": [
                "佇列（Queue）是一種先進先出（FIFO）的資料結構，類似排隊。元素從佇列尾端加入，從佇列前端移出。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "佇列(Queue)的基本操作有哪些？",
             "Answer": [
                "佇列的基本操作包括：enqueue將元素加入佇列尾端、dequeue移除第一個元素、front/peek檢查第一個元素和isEmpty檢查佇列是否為空。"
              ],
              "Type": "開放式問題"
            }

        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
