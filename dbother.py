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
            {"Question": "簡短說明整數溢位(integer overflow)的避免方法。",
             "Answer": [
                "為了避免整數溢位，可以使用較大範圍的資料型別，如`long`或`BigInteger`，來儲存可能超過基本整數範圍的數字。此外，實施邊界檢查，確保在運算前確認數值不會導致溢位也是有效的方法。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "靜態陣列和動態陣列有何差異？指出其優缺點。",
             "Answer": [
                "靜態陣列大小固定，記憶體分配在編譯時，速度快但不靈活且浪費空間；動態陣列大小可變，記憶體分配在執行時，靈活性高但速度較慢。靜態陣列適合固定數據，動態陣列適合不確定數量的數據。"
             ],
             "Type": "開放式問題"
             },
            {"Question": "請簡短說明傳值呼叫(call by value)。",
             "Answer": [
                "傳值呼叫是指在函數呼叫時，將變數的值複製一份再傳入函數中。在函數內部對變數的改變不會影響到外部的原始變數，確保了原始資料的安全但可能增加記憶體使用。"
              ],
             "Type": "開放式問題"
            },
            {"Question": "請簡短說明繼承(inheritance)。",
             "Answer": [
                "繼承是一種面向物件編程的概念，指的是一個類別可以繼承另一個類別的屬性和方法，從而建立父類別和子類別的關係。子類別繼承父類別的所有成員（屬性和方法），並可以新增或覆寫父類別的成員。"
             ],
             "Type": "開放式問題"
            },
            {"Question": "請簡短說明Overloading。",
             "Answer": [
                "Overloading 是指在程式設計中，允許同一個函式或運算符根據不同的參數類型或數量執行不同的操作。例如，C++ 中可以有多個同名函式，但其參數不同，這樣程式可以更靈活地處理各種情況。"
            ],
             "Type": "開放式問題"
            },
            {"Question": "請簡短說明傳址呼叫(call by address)。",
             "Answer": [
                "傳址呼叫是一種參數傳遞方式，當函數被呼叫時，實際參數的地址會傳遞給函數。這樣，函數可以直接訪問和修改原始變數的值，適合需要改變變數內容的情況。"
             ],
             "Type": "開放式問題"
            },
            {"Question": "請簡短說明傳參考呼叫(call by reference)。",
             "Answer": [
                "傳參考呼叫是指在函式中傳遞變數的地址，這樣在函式內部修改該變數時，原始變數也會被改變。這種方式可以節省記憶體和提高效能。"
             ],
             "Type": "開放式問題" 
            },
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
