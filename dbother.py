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
            {"Question": "試描述整數溢位integer overflow的避免方法，並寫出C++程式碼", "Answer": "xx"},
            {"Question": "如何幫陣列元素設定非零的初始值？須寫出C++程式碼。", "Answer": "xx"},
            {"Question": "靜態陣列和動態陣列有何差異？指出其優缺點。", "Answer": "xx"},
            {"Question": "寫出C++程式碼說明傳值呼叫call by value。", "Answer": "xx"},
            {"Question": "寫出C++程式碼說明兩個類別間的繼承inheritance。", "Answer": "xx"},
            {"Question": "寫出C++程式碼說明同類別兩個方法如何實現多載overloading。", "Answer": "xx"},
            {"Question": "傳入陣列A和整數S，寫出C++函數從A找三個數字加總為S的組合。", "Answer": "xx"},
            {"Question": "寫C++程式碼說明傳址呼叫call by address。", "Answer": "xx"},
            {"Question": "寫出可以精準描述自己學號(如字串10927188)的文法grammar。", "Answer": "xx"},
            {"Question": "寫C++程式碼介紹一組讀檔和寫檔的指令，須能成功編譯執行。", "Answer": "xx"},
            {"Question": "寫Python程式碼實現近似C++ class隱藏資料的效果，並指出差異。", "Answer": "xx"},
            {"Question": "寫C++程式碼說明傳參考呼叫call by reference。", "Answer": "xx"}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
