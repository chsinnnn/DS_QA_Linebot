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
            {"Question": "舉例說明單一佇列模擬如何計算平均等候時間waiting time。", "Answer": "xx"},
            {"Question": "舉例說明單一佇列模擬如何計算平均佇列長度queue length。", "Answer": "xx"},
            {"Question": "舉例說明雙重佇列如何模擬，須指出選擇佇列的策略。", "Answer": "xx"},
            {"Question": "舉例說明多重佇列如何模擬，須指出選擇佇列的策略。", "Answer": "xx"},
            {"Question": "提出二種選擇佇列的策略，並舉例比較二者。", "Answer": "xx"}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
