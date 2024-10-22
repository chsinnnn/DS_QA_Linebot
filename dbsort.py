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
            {"Question": "說明氣泡排序(bubble sort)如何提早結束執行。",
             "Answer": [
                "氣泡排序可以透過在每一輪檢查是否有元素交換，若無交換，代表已經排序完成，提早結束排序，避免不必要的比較。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "簡短說明選擇排序(selection sort)為什麼不是穩定排序。",
             "Answer": [
                "選擇排序不是穩定排序，因為在選擇最小值時可能會交換不相鄰的相同元素，導致相同值的相對順序被改變，破壞穩定性。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "請指出影響氣泡排序是否穩定的關鍵指令。",
             "Answer": [
                "影響氣泡排序是否穩定的關鍵指令是「交換」，因為氣泡排序只交換相鄰元素，保持相同值的順序不變，所以是穩定排序。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "簡短說明影響插入排序(insertion sort)是否穩定的關鍵指令。",
             "Answer": [
                "插入排序的關鍵指令是「插入」，如果插入過程不改變相同元素的相對位置，排序就是穩定的。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "比較氣泡排序和選擇排序的資料交換次數，何者較多？",
             "Answer": [
                "氣泡排序每次比較時都可能進行資料交換，而選擇排序每次比較後只進行一次資料交換。因此氣泡排序的資料交換次數一般遠多於選擇排序。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "簡短說明何時插入排序的資料搬動次數比希爾排序多？",
             "Answer": [
                "當資料接近反序時，插入排序的搬動次數會比希爾排序多，因為插入排序每次只移動一個元素，而希爾排序能一次大幅調整多個元素位置。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "簡短說明何時希爾排序的資料搬動次數比插入排序多？",
             "Answer": [
                "當資料接近排序完成時，希爾排序的搬動次數可能比插入排序多，因為希爾排序仍需進行多次分組排序，而插入排序在幾乎排序好的情況下搬動較少。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "回答合併排序的遞迴深度和資料筆數的關係。(□□關係)",
             "Answer": [
                "對數關係"
              ],
              "Type": "封閉式問題(有標準答案)"
            },
            {"Question": "簡短說明快速排序的遞迴深度會受何者影響。",
             "Answer": [
                "快速排序的遞迴深度受選擇樞紐（pivot）的好壞影響，若樞紐選得不好，遞迴深度會加深。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "簡短希爾排序為甚麼是不穩定排序。",
             "Answer": [
                "希爾排序是不穩定排序，因為在進行較大間隔的排序時，可能會改變相同鍵值元素的相對順序，導致排序不穩定。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "簡短說明快速排序(quick sort)為甚麼是不穩定排序。",
             "Answer": [
                "快速排序是不穩定排序，因為在分區時，可能會改變相同鍵值元素的相對順序，導致排序後順序發生變化。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "為快速排序提出選擇樞紐(pivot)的方法，並簡短說明優點。",
             "Answer": [
                "快速排序選擇基準（pivot）的方法有：使用首尾元素、隨機選取或三數取中法。隨機選取能避免最壞情況，三數取中法則能更平衡分割數組，提升效率。"
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
    
