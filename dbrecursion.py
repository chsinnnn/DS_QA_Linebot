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
        collection = db.recursion
        data = [
            {"Question": "以自己的話描述遞迴recursion是什麼"},
            {"Question": "遞迴呼叫為何會造成記憶體區段錯誤？"},
            {"Question": "若遞迴到某層就異常終止，要如何強制它繼續執行到下一層？"},
            {"Question": "什麼情況下適合使用遞迴？為什麼？"}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
