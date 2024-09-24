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
            {"Question": "以自己的話描述遞迴(recursion)是什麼",
             "Answer": [
                "遞迴是一種程式設計技術，透過函數自我呼叫來解決問題。",
                "遞迴會將問題分解成更小的子問題，重複進行直到達到基礎條件停止。"
            ]},
            {"Question": "遞迴呼叫為何會造成記憶體區段錯誤？",
             "Answer": [
                "遞迴呼叫會造成記憶體區段錯誤，是因為遞迴層數過多，導致系統堆疊空間耗盡，進而觸發記憶體存取違規。",
                "遞迴呼叫可能造成記憶體區段錯誤，是因為每次呼叫都會在記憶體中分配新的堆疊空間，如果沒有正確終止或限制，會導致堆疊溢位，從而出錯。"
            ]},
            {"Question": "若遞迴到某層就異常終止，要如何強制它繼續執行到下一層？",
             "Answer":[
                "如果遞迴到某層異常終止，可以在遞迴函式內部加上錯誤處理機制，例如使用 try-catch 來捕捉錯誤，確保異常不會影響到其他層的執行。",
                "可以在遞迴的每層加上異常處理機制，比如 try...except，這樣即使遇到異常，也可以繼續執行下一層的遞迴。"
            ]},
            {"Question": "什麼情況下適合使用遞迴？為什麼？",
             "Answer": [
                "當問題可以被分解為相同或相似的子問題時，使用遞迴是適合的。因為遞迴可以簡化代碼並使解決方案更具可讀性。",
                "遞迴適合用來解決問題可以分解成更小、相似子問題的情況，例如：階乘計算和樹狀結構遍歷。"
            ]},
            {"Question": "遞迴(recursion)和迴圈(interative)的區別是什麼？",
             "Answer": [
                "遞迴和迴圈都是用來重複執行代碼的結構，區別在於遞迴是函數自我呼叫，而迴圈是通過迭代實現。",
            ]},
            {"Question": "遞迴的基本條件是什麼？",
             "Answer": [
                "遞迴的基本條件是指遞迴停止的條件，當滿足這個條件時，遞迴不再繼續呼叫自身。",
                "基本條件是遞迴結束的條件，防止遞迴無限進行，通常是最簡單的情況或問題的最小單位。"
            ]},
            {"Question": "遞迴的優缺點是什麼？",
             "Answer": [
                "優點：遞迴可以使代碼更簡潔，易於理解和維護，特別是用於解決可以分解為相似子問題的問題。",
                "缺點：遞迴可能會導致較高的記憶體消耗和較低的執行效率，特別是在遞迴深度較大時，可能會導致堆疊溢位。"
            ]},
            {"Question": "遞迴沒有終止條件會發生什麼事？",
             "Answer": [
                "如果遞迴沒有終止條件，遞迴將一直遞迴下去，直到系統堆疊耗盡，導致堆疊溢位，程序異常終止。"
            ]}
            
            



        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
