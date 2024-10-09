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
                "在二元搜尋樹中，若出現相同搜尋鍵，通常將新資料插入右子樹或設計為允許重複鍵的樹。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "已排序資料如何建立一棵平衡的二元搜尋樹？",
             "Answer": [
                "將已排序的資料中位數作為根節點，將左半部分資料作為左子樹，右半部分作為右子樹，遞迴重複此過程，即可建立平衡的二元搜尋樹。"
             ],
             "Type": "開放式問題"
             },
            {"Question": "舉例說明如何為二元搜尋樹刪除節點。",
             "Answer": [
                "刪除二元搜尋樹節點有三種情況：1. 無子節點，直接刪除。2. 一個子節點，用子節點替代。3. 兩個子節點，用後繼節點替代。"
              ],
             "Type": "開放式問題"
            },
            {"Question": "簡短說明二元搜尋樹和堆積(heap)的差異。",
             "Answer": [
                "二元搜尋樹是按大小排序的樹結構，左子樹小於根，右子樹大於根；堆積則是一種完全二元樹，根節點是最大或最小值。"
             ],
             "Type": "開放式問題"
            },
            {"Question": "說明堆積排序(heap sort)是否為穩定排序。",
             "Answer": [
                "堆積排序不是穩定排序，因為相同鍵值的元素在排序過程中，可能會改變相對順序。"
            ],
             "Type": "開放式問題"
            },
            {"Question": "說明使用陣列實作堆積結構的優缺點。",
             "Answer": [
                "使用陣列實作堆積結構的優點是存取速度快、記憶體連續，但缺點是大小固定，擴充困難，且需要事先知道所需空間。"
             ],
             "Type": "開放式問題"
            },
            {"Question": "說明使用指標實作堆積結構的優缺點。",
             "Answer": [
                "使用指標實作堆積的優點是靈活，可動態調整大小；缺點是需額外儲存指標，浪費記憶體空間，且操作較複雜。"
            ],
            "Type": "開放式問題" 
            },
            {"Question": "說明完全二元樹、完整二元樹及平衡二元樹的特性。",
             "Answer": [
                "完全二元樹：所有層滿或最後一層從左到右填滿。完整二元樹：每個節點都有兩個或零個子節點。平衡二元樹：所有子樹高度差不超過1。"
             ],
             "Type": "開放式問題" 
            },
            {"Question": "說明使用前序(preorder)、中序(inorder)及後序(postorder)如何走訪二元樹。",
             "Answer": [
                "前序走訪是先訪問根節點，再訪左子樹，最後訪右子樹；中序走訪是先訪左子樹，再訪根節點，最後訪右子樹；後序走訪則是先訪左子樹，再訪右子樹，最後訪根節點。",
             ],
             "Type": "開放式問題"
            },
            {"Question": "說明使用中序走訪二元搜尋樹是否為穩定排序。",
             "Answer": [
                "中序走訪二元搜尋樹是穩定排序，因為遍歷結果會按鍵值的遞增順序輸出，且不改變相同鍵值的相對順序。"
             ],
             "Type": "開放式問題"
             },
            {"Question": "簡短說明二元搜尋樹如何搜尋節點",
             "Answer": [
                 "在二元搜尋樹中，搜尋節點時，從根節點開始，比較目標值與當前節點的值。如果目標值較小，則向左子樹繼續搜尋；如果較大，則向右子樹搜尋，直到找到節點或到達空子樹為止。"
             ],
             "Type": "開放式問題"
            },
            {"Question": "簡短說明二元搜尋樹如何平衡",
             "Answer": [ 
                 "二元搜尋樹可以使用AVL樹或紅黑樹等方法平衡。這些樹在插入或刪除節點後會進行旋轉操作，確保樹的高度差不超過1，維持搜尋效率。"
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
    
