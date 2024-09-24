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
             "Answer": [
                "中序式是(((a + b) * c) * ((d + e) * (f + (w + z))))"
            ]},
            {"Question": "將後序式(postfix)轉前序式(prefix)。a b + c * d e + f * + w z + *",
             "Answer": [
                "* + + a b * + c + d e * f + w z"
            ]},
            {"Question": "合法運算式若有三組括弧，可以有幾種不同的形式？例如()()()和(()())就是二種不同的形式。",
             "Answer": [
                "合法運算式有三組括號時，可以有5種不同的形式"
            ]},
            {"Question": "+ * 2 4 6 * - 7 5是前序式嗎？為什麼？",
             "Answer": [
                "不是，因為運算元的數量不正確。前序式需要每個運算元都有對應的運算符，才能正確計算。"
            ]},
            {"Question": "算出後序式2 4 6 * + 7 5 - *的正確答案",
             "Answer": [
                "52"
            ]},
            {"Question": "堆疊(stack)的特性是什麼？",
             "Answer": [
                "堆疊是一種先進後出的資料結構，只能在堆疊的頂端進行操作。"
            ]},
            {"Question": "堆疊的操作有哪些？",
             "Answer": [
                "堆疊的操作包括push(新增)、pop(刪除)、top(取頂端元素)、empty(判斷是否為空)等。"
            ]},
            {"Question": "堆疊的時間複雜度是多少？",
             "Answer": [
                "堆疊的時間複雜度是O(1)，因為堆疊的操作都是在頂端進行的。"
            ]},
            
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
