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
            {"Question": "令ptrX指向鏈結串列的節點，比較ptrX = ptrX->next和ptrX->next = ptrX的差異。",
             "Answer": [
                "ptrX = ptrX->next 會讓指標指向下一個節點；ptrX->next = ptrX 會讓當前節點的 next 指標指向自己，可能會造成迴圈或錯誤。兩者功能和效果不同。"
            ]},
            {"Question": "舉例說明使用雙向鏈結串列doubly linked list的情境。",
             "Answer": [
                "雙向鏈結串列適合需要頻繁在列表中間插入或刪除項目的情境，比如音樂播放器的播放列表。它可以方便地在前後兩端和中間進行操作。",
                "雙向鏈結串列常用於需要頻繁前後移動的情境，比如編輯器中的文本行。因為它允許從兩個方向快速遍歷，方便在中間插入或刪除文本。"
            ]},
            {"Question": "舉例說明使用環狀鏈結串列Circularly linked list的情境。",
             "Answer": [
                "環狀鏈結串列常用於需要無限循環的情境，如模擬圓形遊戲的玩家輪流出牌，或連續播放音樂播放列表，每次回到起點後仍能繼續循環。"
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
