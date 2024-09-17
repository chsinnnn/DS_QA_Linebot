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
            {"Question": "試描述整數溢位integer overflow的避免方法",
             "Answer": [
                "整數溢位可以通過使用更大的數據類型（如long或bigint）或在計算前檢查數值範圍來避免。這樣可以確保運算結果不會超過數據型別的上限。",
                "整數溢位可以用以下方法避免：選擇更大的數據類型，檢查數值範圍，使用安全的數學函式。並在計算前後進行檢查，以確保不超過預期範圍。"
            ]},
            {"Question": "靜態陣列和動態陣列有何差異？指出其優缺點。",
             "Answer": [
                "靜態陣列大小在編譯時決定，存儲於stack，速度快但無法調整大小，靈活性差。動態陣列大小可在運行時調整，存儲於heap，靈活且能適應數據變化，但需要手動管理記憶體，可能導致記憶體碎片，且管理複雜。"
            ]},
            {"Question": "說明傳值呼叫call by value是甚麼。",
             "Answer": [
                "傳值呼叫是指在函式呼叫時，將變數的值複製一份傳遞給函式。這樣一來，即使函式內部修改了參數值，原本的變數也不會受到影響。"
            ]},
            {"Question": "說明繼承inheritance是甚麼。",
             "Answer":[
                "繼承是物件導向程式設計中的一種技術，讓子類別可以繼承父類別的屬性和方法，這樣子類別就能重複使用父類別的代碼，並可以新增或修改功能。",
                "Inheritance繼承是指子類別可以繼承父類別的屬性和方法，讓子類別可以使用父類別的功能，減少程式碼重複。"
            ]},
            {"Question": "何為Overloading?",
             "Answer": [
                "Overloading指的是在同一個程式中，定義多個名稱相同但參數不同的函式或方法。這樣可以讓程式更靈活，根據不同的需求選擇合適的版本。"
            ]},
            {"Question": "說明傳址呼叫call by address",
             "Answer": [
                "傳址呼叫是將變數的記憶體位址傳遞給函數，使函數可以直接修改該變數的原始值，而不需要複製數據。"
            ]},
            {"Question": "說明傳參考呼叫call by reference是甚麼。",
             "Answer":[
                "傳參考呼叫是將變數的記憶體位置傳給函數，讓函數可以直接修改原變數的值。這樣改變在函數內做出的變動會反映到原變數上。"
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
