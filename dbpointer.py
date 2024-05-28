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
        collection = db.pointer
        data = [
            {"Question": "令ptrX指向鏈結串列的節點，比較ptrX = ptrX->next和ptrX->next = ptrX的差異。", "Answer": "xx"},
            {"Question": "寫C++程式碼說明刪除鏈結串列linked list第3個節點。", "Answer": "xx"},
            {"Question": "舉例說明使用雙向鏈結串列doubly linked list的情境。", "Answer": "xx"},
            {"Question": "舉例說明使用環狀鏈結串列Circularly linked list的情境。", "Answer": "xx"},
            {"Question": "寫C++程式碼設計遞迴函數產生3個數字不同且加總等於M的所有3位數，M是輸入的整數，百位數必須非零。", "Answer": "xx"},
            {"Question": "寫C++程式碼說明如何複製一整個鏈結串列linked list到另一個變數。", "Answer": "xx"}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
