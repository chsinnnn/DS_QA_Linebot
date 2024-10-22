from pymongo import MongoClient
from pprint import pprint

def connect_to_database():
    try:
        client = MongoClient("mongodb://localhost:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.5")
        db = client.teststudentdata
        print("Connected to MongoDB")
        return db
    except Exception as error:
        print("Failed to connect to MongoDB:", error)
        return None


def calculate_average_score(student_scores):
    total_score = sum(student["評分"] for student in student_scores)
    if len(student_scores) > 0:
        return total_score / len(student_scores)
    return 0

def create_new_data(db):
    try:
        collection = db.firstclass
        data = [
            {
                "Question": "如果ptrX是鏈結串列中的一個節點，請說明ptrX = ptrX->next和ptrX->next = ptrX有什麼不同。",
                "studentans_score": [
                    {
                        "學號": "11027149",
                        "評分": 0,
                        "答案": "不知道",
                        "評語": ""
                    }
                ]
            },
            {
                "Question": "簡短說明整數溢位(integer overflow)的避免方法。",
                "studentans_score": [
                    {
                        "學號": "11027149",
                        "評分": 0,
                        "答案": "不知道我不會",
                        "評語": ""
                    },
                    {
                        "學號": "11027150",
                        "評分": 1,
                        "答案": "整數溢位可以透過減少數字大小或加大儲存空間來避免。",
                        "評語": ""
                    },
                    {
                        "學號": "11027152",
                        "評分": 2,
                        "答案": "整數溢位可以透過使用較大範圍的資料型別、在運算前檢查數值範圍，或使用程式語言內建的溢位檢查工具來避免。",
                        "評語": ""
                    }
                ]
            },
            {
                "Question": "請簡短說明Overloading。",
                "studentans_score": [
                    {
                        "學號": "11027149",
                        "評分": 0,
                        "答案": "不知道",
                        "評語": ""
                    },
                    {
                        "學號": "11027122",
                        "評分": 0,
                        "答案": "不知道",
                        "評語": ""
                    },
                    {
                        "學號": "11027111",
                        "評分": 0,
                        "答案": "不知道",
                        "評語": ""
                    },
                    {
                        "學號": "11027150",
                        "評分": 2,
                        "答案": "同一個函式或運算符根據不同的參數類型或數量執行不同的操作",
                        "評語": ""
                    },
                    {
                        "學號": "11027152",
                        "評分": 2,
                        "答案": "同一個函式或運算符根據不同的參數類型或數量執行不同的操作",
                        "評語": ""
                    }
                ]
            }
        ]

        # 計算平均分數並插入
        for question in data:
            question["平均分數"] = calculate_average_score(question["studentans_score"])
            result = collection.insert_one(question)
            pprint(result.inserted_id)
    except Exception as error:
        print("Error inserting data:", error)

if __name__ == "__main__":
    db = connect_to_database()
    if db is not None:
        create_new_data(db)
