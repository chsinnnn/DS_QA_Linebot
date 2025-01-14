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
             "Answer": [
                "遞迴是函式自己呼叫自己的概念，通常用來解決可以分成相似子問題的大問題，直到達到初始情況停止。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "遞迴呼叫為何會造成記憶體區段錯誤？",
             "Answer": [
                "遞迴若無停止條件或深度過大，會不斷占用堆疊記憶體，導致堆疊溢位，進而引發記憶體區段錯誤。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "若遞迴到某層就異常終止，要如何強制它繼續執行到下一層？",
             "Answer": [
                "可使用條件判斷或例外處理（如try-catch）來處理異常，確保遞迴能跳過錯誤並繼續執行下一層。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "什麼情況下適合使用遞迴？為什麼？",
             "Answer": [
                "當問題可以被分解為相似的小問題，且有明確的結束條件時，適合使用遞迴，因為它能簡化程式邏輯。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "遞迴(recursion)和迴圈(interative)的區別是什麼？",
             "Answer": [
                "遞迴是函數自己呼叫自己，直到滿足終止條件，適合分解問題。迴圈則是重複執行某段程式碼，用條件控制結束。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "遞迴的基本條件是什麼？",
             "Answer": [
                "遞迴的基本條件是：問題可以被分解、小問題結構相同，並且需要有明確的終止條件來避免無限遞迴。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "遞迴沒有終止條件會發生什麼事？",
             "Answer": [
                "遞迴沒有終止條件會導致函數無限呼叫自己，導致程式陷入無限遞迴，最終造成記憶體耗盡。"
              ],
              "Type": "開放式問題"
            }
            
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
