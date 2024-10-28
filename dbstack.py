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
        collection = db.stack
        data = [
            {"Question": "將此後序式(postfix)轉中序式(infix)。a b + c * d e + f * + w z + *",
             "Answer": [
                "((a + b) * c + (d + e) * f) * (w + z)"
              ],
              "Type": "封閉式問題(有標準答案)"
            },
            {"Question": "將後序式(postfix)轉前序式(prefix)。a b + c * d e + f * + w z + *",
             "Answer": [
                "*+*+abc*+def+wz"
              ],
              "Type": "封閉式問題(有標準答案)"
            },
            {"Question": "一個合法的運算式如果有三組括號，可以有多少種不同的排列形式？（回答：O 種，數量以阿拉伯數字表示)",
             "Answer": [
                "5種"
              ],
              "Type": "封閉式問題(有標準答案)"
            },
            {"Question": "* 2 4 6 * - 7 5是前序式嗎？(回答是否)",
             "Answer": [
                "否"
              ],
              "Type": "封閉式問題(有標準答案)"
            },
            {"Question": "算出後序式2 4 6 * + 7 5 - *的正確答案",
             "Answer": [
                "52"
              ],
              "Type": "封閉式問題(有標準答案)"
            },
            {"Question": "堆疊(stack)的特性是什麼？",
             "Answer": [
                "堆疊 (stack) 是一種後進先出 (LIFO) 的資料結構，最後放入的元素最先取出。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "堆疊的操作有哪些？",
             "Answer": [
                "堆疊的操作有：新增元素（push）、刪除元素（pop）、查看頂部元素（top/peek）、檢查是否為空（isEmpty）。"
              ],
              "Type": "開放式問題"
            },
            {"Question": "堆疊的時間複雜度是多少？",
             "Answer": [
                "O(1)"
              ],
              "Type": "封閉式問題(有標準答案)"
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
