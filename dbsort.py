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
        collection = db.sort
        data = [
            {"Question": "說明氣泡排序bubble sort如何提早結束執行。",
             "Answer": [
                "氣泡排序在每一趟排序後會檢查是否有元素交換。若一整趟都沒有發生交換，表示序列已經有序，即可提早結束排序，避免不必要的比較。"
            ]},
            {"Question": "簡短說明選擇排序(selection sort)為什麼不是穩定排序。",
             "Answer": [
                "選擇排序每次都選出未排序部分中最小的元素，並將其放在正確的位置。若有兩個相等的元素，選擇排序可能將它們的相對位置改變，導致排序後相等元素的順序與原先不同，因此選擇排序是不穩定的。"
            ]},
            {"Question": "請指出影響氣泡排序是否穩定的關鍵指令。",
             "Answer":[
                "氣泡排序的穩定性來自於相等元素只在必要時交換，保持其原有的相對順序，從而使氣泡排序是穩定的。"
            ] },
            {"Question": "簡短說明影響插入排序(insertion sort)是否穩定的關鍵指令。",
             "Answer": [
                "插入排序的穩定性關鍵在於相等元素在插入時不交換，保持它們的相對順序，因此插入排序是穩定的。"
            ]},
            {"Question": "比較氣泡排序和選擇排序的資料交換次數，何者較多？",
             "Answer":[
                "氣泡排序每比較一對元素，若順序錯誤就會進行交換，因此交換次數較多。選擇排序每輪只會交換一次，將當前最小值放到正確位置，因此交換次數較少。"
            ]},
            {"Question": "簡短說明何時插入排序的資料搬動次數比希爾排序多？",
             "Answer": [
                "當數列接近反序時，插入排序的資料搬動次數比希爾排序多，因為希爾排序會先分組減少搬動次數。"
            ]},
            {"Question": "簡短說明何時希爾排序的資料搬動次數比插入排序多？",
             "Answer": [
                "希爾排序選擇不佳的間隔序列如 [1, 2, 3, 4, 5],，搬動次數可能較插入排序多。"
            ]},
            {"Question": "簡短說明合併排序的遞迴深度和資料筆數的關係。",
             "Answer": [
                "合併排序的遞迴深度與資料筆數呈對數關係。"
            ]},
            {"Question": "簡短說明快速排序的遞迴深度會受何者影響。",
             "Answer": [
                "快速排序的遞迴深度受樞紐pivot選擇影響。選擇不佳，最差情況下遞迴深度為 n。"
            ]},
            {"Question": "簡短希爾排序為甚麼是不穩定排序。", 
             "Answer": [
                "希爾排序並非穩定。例：排序 [3a, 2, 3b],，間隔為2時，3a 和 3b 可能被交換，改變相對順序。",
                "希爾排序是非穩定排序，因為在分組排序過程中，相同元素的相對順序可能會改變"
            ]},
            {"Question": "簡短說明快速排序(quick sort)為甚麼是不穩定排序。",
             "Answer": [
                "快速排序並非穩定。例：排序 [3a, 2, 3b],，選 2 為基準，分區後可能 3a 和 3b 交換，改變相對順序。",
                "快速排序是不穩定的。例如，有兩個相等元素A和B，若A在B前面，在分區過程中，A和B可能被分到不同的子陣列，導致排序後A和B的相對位置發生改變，因此快速排序不保證相等元素的相對順序不變。"
            ]},
            {"Question": "為快速排序提出選擇基準pivot的方法，並簡短說明優點。",
             "Answer": [
                "選擇基準(pivot)的方法：三數取中法（如選首、中、尾三數的中間值）。優點：減少最差情況概率，提供較均勻分區。"
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
    
