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
        collection = db.pointer
        data = [
            {"Question": "如果ptrX是鏈結串列中的一個節點，請說明ptrX = ptrX->next和ptrX->next = ptrX有什麼不同。",
             "Answer": [
                "ptrX = ptrX->next 將 ptrX 移動到下一個節點；而 ptrX->next = ptrX 將當前節點的下一個指向自己，可能導致循環鏈結。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "如何釋放指標所指向的記憶體？",
             "Answer": [
                "要釋放指標指向的記憶體，可以使用 free() 函數。首先確認指標不為 NULL，然後呼叫 free(指標)，這樣就能釋放指標所佔用的記憶體空間。使用delete釋放指標所指向的記憶體，若是陣列則用delete[]。記憶體釋放後應將指標設為nullptr，避免野指標問題。"
              ],
              "Type": "開放式問題"
            },            
            {"Question": "什麼是指標(pointer)？",
             "Answer": [
                "指標是一種變數，用來儲存記憶體位址，可以直接訪問或操作該位址中的數據。在程式中，指標能提高效率，特別是在處理大型數據結構時。"
              ],
              "Type": "開放式問題"
            },            
            {"Question": "請舉一個適合使用雙向鏈結串列(doubly linked list)的例子。",
             "Answer": [
                "一個適合使用雙向鏈結串列的例子是音樂播放器的播放列表。這樣可以方便地從當前曲目向前或向後切換，並且能夠輕鬆地插入或刪除曲目。"
              ],
              "Type": "開放式問題"
            },            
            {"Question": "什麼是空指標(null pointer)？",
             "Answer": [
                "空指標（null pointer）是一種不指向任何有效記憶體位置的指標，通常用來表示指標未初始化或不指向任何物件。"
              ],
              "Type": "開放式問題"
            },            
            {"Question": "如何宣告和初始化一個指標變數？",
             "Answer": [
                "要宣告和初始化一個指標變數，可以這樣寫：int *ptr = null;"
              ],
              "Type": "開放式問題"
            },            
            {"Question": "請舉一個適合使用環狀鏈結串列(Circularly linked list)的例子。",
             "Answer": [
                "環狀鏈結串列適合用於音樂播放器的播放清單，因為可以不斷循環播放歌曲，當到達最後一首歌時，自動返回到第一首實現循環播放的功能。"
              ],
              "Type": "開放式問題"
            },            
            {"Question": "什麼是單向鏈結串列(singly linked list)？",
             "Answer": [
                "單向鏈結串列是一種資料結構，其中每個節點只包含資料和一個指向下一個節點的指標，方向是單向的。"
              ],
              "Type": "開放式問題"
            },            
            {"Question": "什麼是鏈結串列(linked list)？",
             "Answer": [
                "鏈結串列是一種資料結構，由一連串節點組成，每個節點包含資料和指向下一個節點的指標，用來動態管理資料，方便插入和刪除元素。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "什麼是雙向鏈結串列(doubly linked list)？",
             "Answer": [
                "雙向鏈結串列是一種資料結構，其中每個節點包含資料以及指向前一個和下一個節點的指標，允許在兩個方向上遍歷。"
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
