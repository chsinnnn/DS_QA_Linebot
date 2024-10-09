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
            {"Question": "以自己的話描述遞迴(recursion)是什麼。",
            "Answer": ["遞迴是函數自己調用自己的方式，用來解決問題。通常會有一個基礎條件，讓遞迴停止，避免無限循環。"],
            "Type": "開放式問題"},
            {"Question": "遞迴呼叫為何會造成記憶體區段錯誤？",
            "Answer": ["遞迴呼叫太深時，會用掉大量記憶體堆疊空間，超出系統限制，導致記憶體區段錯誤（Stack Overflow）。"],
            "Type": "開放式問題"},
            {"Question": "若遞迴到某層就異常終止，要如何強制它繼續執行到下一層？",
            "Answer": ["可使用條件判斷或例外處理（如try-catch）來處理異常，確保遞迴能跳過錯誤並繼續執行下一層。"],
            "Type": "開放式問題"},
            {"Question": "什麼情況下適合使用遞迴？為什麼？",
            "Answer": ["當問題能被分解為相似的子問題時適合使用遞迴，如樹遍歷或費氏數列，因為遞迴能讓程式簡潔易懂。"],
            "Type": "開放式問題"},
            {"Question": "遞迴(recursion)和迴圈(interative)的區別是什麼？",
            "Answer": ["遞迴是函數自我調用解問題，迴圈是用控制結構重複執行程式碼。遞迴更直觀解子問題，但迴圈通常效率更高。"],
            "Type": "開放式問題"},
            {"Question": "遞迴的基本條件是什麼？",
            "Answer": ["遞迴的基本條件包括兩點：1. 基底條件（Base Case），用來終止遞迴；2. 遞迴關係，問題逐步縮小並遞迴調用自身。"],
            "Type": "開放式問題"},
            {"Question": "遞迴沒有終止條件會發生什麼事？",
            "Answer": ["遞迴如果沒有終止條件，函數會不停地呼叫自己，導致程式陷入無限遞迴，最終可能導致堆疊溢位(Stack Overflow)並使程式崩潰。"],
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
