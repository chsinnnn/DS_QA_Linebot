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
            {"Question": "令ptrX指向鏈結串列的節點，比較ptrX = ptrX->next和ptrX->next = ptrX的差異。"},
            {"Question": "舉例說明使用雙向鏈結串列doubly linked list的情境。"},
            {"Question": "舉例說明使用環狀鏈結串列Circularly linked list的情境。"}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
