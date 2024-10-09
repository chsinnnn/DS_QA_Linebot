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
            {"Question": "將此後序式(postfix)轉中序式(infix)。a b + c * d e + f * + w z + *",
            "Answer": ["結果為：((a + b) * c + (d + e) * f) * (w + z)"],
            "Type": "開放式問題"},
            {"Question": "* 2 4 6 * - 7 5是前序式嗎？(回答是否)",
            "Answer": ["* 2 4 6 * - 7 5 不是合法的前序式。前序式需要運算符在前，並且每個運算符應有足夠的操作數，此式無法正確對應運算。"],
            "Type": "開放式問題"},
            {"Question": "算出後序式2 4 6 * + 7 5 - *的正確答案",
            "Answer": ["後序式的計算順序是先處理運算符前的兩個數字。計算過程如下：\n\n1. 6 * 4 = 24\n2. 2 + 24 = 26\n3. 7 - 5 = 2\n4. 26 * 2 = **52**\n\n最終答案是52。"],
            "Type": "開放式問題"},
            {"Question": "堆疊(stack)的特性是什麼？",
            "Answer": ["堆疊 (stack) 是一種後進先出 (LIFO) 的資料結構，最後放入的元素最先取出。"],
            "Type": "開放式問題"},
            {"Question": "堆疊的操作有哪些？",
            "Answer": ["堆疊的操作有：新增元素（push）、刪除元素（pop）、查看頂部元素（top/peek）、檢查是否為空（isEmpty）。"],
            "Type": "開放式問題"},
            {"Question": "堆疊的時間複雜度是多少？",
            "Answer": ["堆疊的基本操作如推入（push）、彈出（pop）、查看頂部（top）和檢查是否為空（isEmpty）的時間複雜度都是 O(1)。"],
            "Type": "開放式問題"}
            ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
