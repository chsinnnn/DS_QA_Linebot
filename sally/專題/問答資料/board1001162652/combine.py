import os
import json
import re

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def clean_html_content(html_content):
    """清理HTML標籤和多餘字符"""
    cleanr = re.compile('<.*?>')
    clean_text = re.sub(cleanr, '', html_content)
    clean_text = clean_text.replace('\r\n', ' ').replace('&nbsp;', ' ').replace('&quot;', ' ').strip()
    return clean_text

def match_questions_answers_comments(responses_folder, output_file):
    answers = {}
    comments = {}

    # 定義題目對應
    questions = {
        "101": "以自己的話描述遞迴recursion是什麼。",
        "102": "試寫出一個遞迴函數找出一群整數的中位數median。",
        "103": "簡介Acker函數，並列出Acker(2,3)的求解過程。",
        "104": "什麼情況下適合使用遞迴？為什麼？",
        "105": "試描述整數溢位integer overflow的避免方法，並寫出C++程式碼。"
    }

    # 讀取所有的 JSON 檔案
    for filename in os.listdir(responses_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(responses_folder, filename)
            data = load_json_file(file_path)
            file_id = filename.split('.')[0]

            # 確定這是一個答案還是評論
            if len(file_id) == 10:  # 這是一個答案
                answers[file_id] = data
            elif len(file_id) > 10:  # 這是一個評論
                comments[file_id] = data

    # 準備LLaMA3模型數據
    llama3_data = []
    for answer_id, answer_data in answers.items():
        response_node = answer_data['data']['node']
        answer_content = clean_html_content(answer_data['data']['content'])
        subject = answer_data['data']['subject']

        # 根據 subject 中的編號加上對應的題目內容
        question_content = ""
        for key in questions:
            if key in subject:
                question_content = questions[key]
                break

        full_answer = f"題目: {question_content}答案: {answer_content}"

        # 搜集所有評論
        answer_comments = []
        for comment_id, comment_data in comments.items():
            comment_node = comment_data['data']['node']
            parent_node = comment_id[:10]  # 取前10個字符作為父節點ID
            if parent_node == answer_id:
                comment_content = clean_html_content(comment_data['data']['content'])
                answer_comments.append(comment_content)

        # 準備數據輸出格式
        llama3_data.append({
            "instruction": "請根據以下問題的回答作出評論，並判斷回答是否正確",
            "input": full_answer,
            "output": " ".join(answer_comments)
        })

    # 儲存LLaMA3模型數據到輸出的 JSON 檔案
    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(llama3_data, output, ensure_ascii=False, indent=4)

    print(f'Combined JSON file saved to {output_file}')

# 指定你的 JSON 資料夾和輸出檔案名稱
responses_folder = 'C:/Users/sally/Desktop/專題/問答資料/board1001162652/json'
output_file = 'C:/Users/sally/Desktop/專題/問答資料/board1001162652/llama3_board1001162652.json'

match_questions_answers_comments(responses_folder, output_file)
