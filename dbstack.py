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
        collection = db.stack
        data = [
            {"Question": "將此後序式postfix轉中序式infix。a b + c * d e + f * + w z + *"},
            {"Question": "將後序式postfix轉前序式prefix。a b + c * d e + f * + w z + *"},
            {"Question": "合法運算式若有三組括弧，可以有幾種不同的形式？例如()()()和(()())就是二種不同的形式。"},
            {"Question": "+ * 2 4 6 * - 7 5是前序式嗎？為什麼？"},
            {"Question": "算出後序式2 4 6 * + 7 5 - *的正確答案"}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
