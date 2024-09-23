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
                "ptrX = ptrX->next 會讓指標指向下一個節點；ptrX->next = ptrX 會讓當前節點的 next 指標指向自己，可能會造成迴圈或錯誤。兩者功能和效果不同。"
            ]},
            {"Question": "如何釋放指標所指向的記憶體？",
             "Answer": [
                "在C/C++中，可以使用free()函數來釋放指標所指向的記憶體。釋放後，應將指標設為NULL以避免懸空指標。"
            ]},
            {"Question": "什麼是指標(pointer)？",
             "Answer": [
                "指標是一種變數，用於存儲另一個變數的記憶體地址。在C/C++等語言中，指標可以用來動態分配記憶體、實現複雜的資料結構和優化程式性能。"
            ]},
            {"Question": "請舉一個適合使用雙向鏈結串列(doubly linked list)的例子。",
             "Answer": [
                "雙向鏈結串列適合需要頻繁在列表中間插入或刪除項目的情境，比如音樂播放器的播放列表。它可以方便地在前後兩端和中間進行操作。",
                "雙向鏈結串列常用於需要頻繁前後移動的情境，比如編輯器中的文本行。因為它允許從兩個方向快速遍歷，方便在中間插入或刪除文本。"
            ]},
            {"Question": "什麼是空指標(null pointer)？",
             "Answer": [
                "空指標是一種特殊的指標，指向記憶體地址0，表示它不指向任何有效的記憶體位置。使用空指標可以避免未初始化指標帶來的錯誤。"
            ]},
            {"Question": "如何宣告和初始化一個指標變數？",
             "Answer": [
                "在C/C++中，可以使用*符號來宣告指標變數。例如：int *ptr; 然後使用&符號來初始化它，例如：int a = 10; ptr = &a; 這樣ptr就指向變數a的記憶體地址。"
            ]},
            {"Question": "請舉一個適合使用環狀鏈結串列(Circularly linked list)的例子。",
             "Answer": [
                "環狀鏈結串列常用於需要無限循環的情境，如模擬圓形遊戲的玩家輪流出牌，或連續播放音樂播放列表，每次回到起點後仍能繼續循環。"
            ]},
            {
             "Question": "什麼是單向鏈結串列(singly linked list)？",
             "Answer": [
                "單向鏈結串列是一種鏈結串列，其中每個節點只包含一個指向下一個節點的指標。它的優點是結構簡單，節省記憶體，但只能從頭到尾遍歷，不能反向遍歷。"
            ]},
            {"Question": "什麼是鏈結串列(linked list)？",
             "Answer": [
                "鏈結串列是一種資料結構，由一系列節點組成，每個節點包含資料和一個指向下一個節點的指標。它的優點是插入和刪除操作效率高，缺點是隨機存取效率低。"
            ]},
            {"Question": "請解釋指標(pointers)的概念及其用途。",
            "Answer": [
                "指標是存放記憶體地址的變數，允許程式直接操作記憶體。它們在動態記憶體分配、數據結構（如鏈結串列、樹等）的實現中非常重要。",
                "指標可用於提高程式的效率，因為可以通過指標傳遞大數據結構，而不需要複製整個結構。"
            ]},
            {"Question": "為什麼雙向鏈結串列在某些情況下效率比單向鏈結串列更高？",
            "Answer": [
                "雙向鏈結串列允許從任意方向遍歷鏈結串列，因此在需要頻繁進行雙向操作時（如插入、刪除或查找某個節點），效率比單向鏈結串列更高。單向鏈結串列只能從頭遍歷到尾，而雙向鏈結串列可以直接從任一位置開始雙向遍歷。",
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
