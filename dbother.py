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
        collection = db.other
        data = [
            {"Question": "試描述整數溢位integer overflow的避免方法"},
            {"Question": "靜態陣列和動態陣列有何差異？指出其優缺點。"},
            {"Question": "說明繼承inheritance是甚麼。"},
            {"Question": "何為Overloading（重載）?"},
            {"Question": "說明傳址呼叫call by address"},
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
