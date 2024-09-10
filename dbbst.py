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
            {"Question": "相同搜尋鍵的二筆資料如何存入二元搜尋樹？"},
            {"Question": "已排序資料如何建立一棵平衡的二元搜尋樹"},
            {"Question": "舉例說明如何為二元搜尋樹刪除節點。"},
            {"Question": "列舉二元搜尋樹和堆積heap的三項差異。"},
            {"Question": "舉例解說堆積排序heap sort是否穩定排序。"},
            {"Question": "比較用陣列或指標實作堆積結構的優缺點。"},
            {"Question": "舉例區別完全full、完整complete及平衡balanced二元樹的差異。"},
            {"Question": "舉例區別前序preorder、中序inorder及後序postorder二元樹走訪的差異"},
            {"Question": "舉例解說中序走訪二元搜尋樹是否穩定排序。"},
            {"Question": "說明二元搜尋樹如何新增節點"}
        ]
        result = collection.insert_many(data)
        pprint(result.inserted_ids)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
    
