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
        collection = db.bst
        data = [
            {"Question": "相同搜尋鍵的二筆資料如何存入二元搜尋樹？",
             "Answer": [
                "每個節點可以使用一個鏈結串列來存儲具有相同鍵值的多筆資料。"
            ]},
            {"Question": "已排序資料如何建立一棵平衡的二元搜尋樹？",
             "Answer": [
                "將已排序資料的中間元素作為根節點，遞迴處理左半部分和右半部分，分別作為左子樹和右子樹。"
            ]},
            {"Question": "舉例說明如何為二元搜尋樹刪除節點。",
             "Answer": [
                "若無子樹，直接刪除。若有一子樹，子樹提升。若有兩子樹，找右子樹最小值替代節點。"
            ]},
            {"Question": "簡短說明二元搜尋樹和堆積(heap)的差異。",
             "Answer": [
                "二元搜尋樹和堆積三項主要差異：結構限制： 二元搜尋樹要求左子樹小於根，右子樹大於根；堆積則要求大根堆子節點小於根，小根堆子節點大於根。主要操作： 二元搜尋樹擅長查找、插入、刪除；堆積則擅長排序、優先佇列。平衡性： 二元搜尋樹可能退化成鏈狀，需額外機制平衡；堆積為完全二元樹，相對平衡。"
            ]},
            {"Question": "說明堆積排序(heap sort)是否為穩定排序。",
             "Answer": [
                "堆積排序不是穩定排序。因為在排序過程中，相同鍵值的元素可能會改變相對位置。"
            ]},
            {"Question": "說明使用陣列實作堆積結構的優缺點。",
             "Answer": [
                "以陣列實作堆積：優點：存取速度快，節省指標空間。缺點：陣列大小固定，擴展不便。"
            ]},
            {"Question": "說明使用指標實作堆積結構的優缺點。",
             "Answer": [
                "以指標實作堆積：優點：動態分配空間，靈活擴展。缺點：存取速度較慢，指標佔用額外空間。"
            ]},
            {"Question": "說明完全二元樹、完整二元樹及平衡二元樹的特性。",
             "Answer": [
                "完全二元樹：每層節點全滿；完整二元樹：每層除最後一層外全滿，最後一層從左到右填滿；平衡二元樹：任一節點兩子樹高度差不超過1"
            ]},
            {"Question": "說明使用前序(preorder)、中序(inorder)及後序(postorder)如何走訪二元樹。",
             "Answer": [
                "前序：根節點先被訪問。中序：根節點在左右子樹之間被訪問。後序：根節點最後被訪問",
                "前序(preorder)：根-左-右,中序(inorder)：左-根-右,後序(postorder)：左-右-根"
            ]},
            {"Question": "說明使用中序走訪二元搜尋樹是否為穩定排序。",
             "Answer": [
                "中序走訪二元搜尋樹是穩定排序。因為二元搜尋樹的特性，左子樹的值小於根節點，右子樹的值大於根節點。中序走訪會先遍歷左子樹，再訪問根節點，最後遍歷右子樹，因此對於相等的值，它們在樹中的相對位置不會改變，排序結果就是穩定的。"
            ]},
            {"Question": "簡短說明二元搜尋樹如何搜尋節點",
             "Answer": ["從根節點開始比較，依大小決定向左或向右子樹移動，直到找到目標節點或空節點。"
            ]},
            {"Question": "簡短說明二元搜尋樹如何平衡",
             "Answer": [ "透過旋轉操作調整不平衡的樹結構，使得左右子樹高度差不超過1。"]}

        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
    
