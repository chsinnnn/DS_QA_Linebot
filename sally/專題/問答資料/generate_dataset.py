import os
import xmltodict
import json
import re

def convert_xml_to_json(xml_folder, json_folder, folder_name):
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    for filename in os.listdir(xml_folder):
        if filename.endswith('.xml'):
            xml_path = os.path.join(xml_folder, filename)
            json_path = os.path.join(json_folder, f"{folder_name}_{filename.replace('.xml', '.json')}")

            with open(xml_path, 'r', encoding='utf-8') as xml_file:
                xml_content = xml_file.read()

            json_content = xmltodict.parse(xml_content)
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_content, json_file, ensure_ascii=False, indent=4)

            print(f'Converted {xml_path} to {json_path}')

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
        "105": "試描述整數溢位integer overflow的避免方法，並寫出C++程式碼。",
        "106": "遞迴呼叫為何會造成記憶體區段錯誤？",
        "107": "作業二採用什麼資料結構儲存讀入資料，須說明原因。",
        "108": "若遞迴到某層就異常終止，要如何強制它繼續執行到下一層？",
        "109": "如何幫陣列元素設定非零的初始值？須寫出C++程式碼。",
        "110": "作業二靜態陣列和動態陣列有何差異？指出其優缺點。",
        "111": "寫出C++程式碼說明傳值呼叫call by value。",
        "112": "寫出C++程式碼說明兩個類別間的繼承inheritance。",
        "113": "將此後序式postfix轉中序式infix，並詳述步驟。a b + c * d e + f * + w z + *",
        "114": "寫出C++程式碼說明同類別兩個方法如何實現多載overloading。",
        "115": "傳入陣列A和整數S，寫出C++函數從A找三個數字加總為S的組合。",
        "116": "將後序式postfix轉前序式prefix，並詳述步驟。a b + c * d e + f * + w z + *",
        "117": "寫C++程式碼說明傳址呼叫call by address。",
        "118": "令ptrX指向鏈結串列的節點，比較ptrX = ptrX->next和ptrX->next = ptrX的差異。",
        "119": "寫C++程式碼說明刪除鏈結串列linked list第3個節點。",
        "120": "舉例說明使用雙向鏈結串列doubly linked list的情境。",
        "121": "舉例說明使用環狀鏈結串列Circularly linked list的情境。",
        "122": "寫C++程式碼說明傳參考呼叫call by reference。",
        "123": "寫C++程式碼說明如何複製一整個鏈結串列linked list到另一個變數。",
        "124": "合法運算式若有三組括弧，可以有幾種不同的形式？例如()()()和(()())就是二種不同的形式。",
        "125": "寫出可以精準描述自己學號(如字串10927188)的文法grammar。",
        "126": "+ * 2 4 6 * - 7 5是前序式嗎？為什麼？",
        "127": "寫C++程式碼介紹一組讀檔和寫檔的指令，須能成功編譯執行。",
        "128": "後序式2 4 6 * + 7 5 - *要如何透過堆疊求解？要列出過程。",
        "129": "寫C++程式碼設計遞迴函數產生3個數字不同且加總等於M的所有3位數，M是輸入的整數，百位數必須非零。",
        "130": "寫Python程式碼實現近似C++ class隱藏資料的效果，並指出差異。",
        "201": "舉例說明單一佇列模擬如何計算平均等候時間waiting time。",
        "202": "舉例說明單一佇列模擬如何計算平均佇列長度queue length。",
        "203": "舉例說明雙重佇列如何模擬，須指出選擇佇列的策略。",
        "204": "舉例說明多重佇列如何模擬，須指出選擇佇列的策略。",
        "205": "提出二種選擇佇列的策略，並舉例比較二者。",
        "206": "撰寫程式碼說明氣泡排序bubble sort如何提早結束執行。",
        "207": "舉例解說選擇排序selection sort並非穩定stable的排序方法。",
        "208": "撰寫程式碼指出影響氣泡排序是否穩定stable的關鍵指令。",
        "209": "撰寫程式碼指出影響插入排序insertion sort是否穩定stable的關鍵指令。",
        "210": "依據程式碼解說選擇排序的時間複雜度。",
        "211": "舉例比較氣泡排序和選擇排序的資料交換swap次數，何者較多？",
        "212": "舉例說明何時插入排序的資料搬動次數比希爾排序shell sort多？",
        "213": "舉例說明何時希爾排序的資料搬動次數比插入排序多？",
        "214": "舉例說明合併排序的遞迴深度和資料筆數的關係。",
        "215": "舉例說明快速排序的遞迴深度會受何者影響。",
        "216": "舉例解說希爾排序shell sort是否穩定stable。",
        "217": "舉例解說快速排序quick sort是否穩定stable。",
        "218": "為快速排序提出選擇基準pivot的方法，並舉例說明優點。",
        "219": "舉例區別完全full、完整complete及平衡balanced二元樹的差異。",
        "220": "舉例區別前序preorder、中序inorder及後序postorder二元樹走訪的差異。",
        "221": "舉例解說中序走訪二元搜尋樹是否穩定排序。",
        "222": "撰寫程式碼指出如何為二元搜尋樹新增節點。",
        "223": "相同搜尋鍵的二筆資料如何存入二元搜尋樹？",
        "224": "如何將二元搜尋樹存檔後再讀入可恢復原狀？",
        "225": "已排序資料如何建立一棵平衡的二元搜尋樹？"
    }

    # 讀取所有的 JSON 檔案
    for filename in os.listdir(responses_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(responses_folder, filename)
            data = load_json_file(file_path)
            file_id = filename.split('.')[0]

            # 確定這是一個答案還是評論
            if len(file_id.split('_')[-1]) == 10:  # 這是一個答案
                answers[file_id] = data
            elif len(file_id.split('_')[-1]) > 10:  # 這是一個評論
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

        full_answer = f"題目: {question_content}  答案: {answer_content}"

        # 搜集所有評論
        answer_comments = []
        for comment_id, comment_data in comments.items():
            comment_node = comment_data['data']['node']
            parent_node = comment_id[:10]  # 取前10個字符作為父節點ID
            if parent_node == answer_id:
                comment_content = clean_html_content(comment_data['data']['content'])
                answer_comments.append(comment_content)

        # 準備數據輸出格式
        output_content = " ".join([f"評論:{comment}" for comment in answer_comments]).strip()
        if output_content:  # 只在 output_content 非空時添加到數據中
            llama3_data.append({
                "instruction": "請根據以下問題的回答作出評論，並判斷回答是否正確",
                "input": full_answer,
                "output": output_content
            })

    # 儲存LLaMA3模型數據到輸出的 JSON 檔案
    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(llama3_data, output, ensure_ascii=False, indent=4)

    print(f'Combined JSON file saved to {output_file}')

def process_all_folders(base_folder, all_data_folder):
    if not os.path.exists(all_data_folder):
        os.makedirs(all_data_folder)

    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        if os.path.isdir(folder_path):
            board_folder = os.path.join(folder_path, 'board')
            if not os.path.exists(board_folder):
                continue
            json_folder = os.path.join(folder_path, 'json')
            output_file = os.path.join(all_data_folder, f'{folder_name}_data.json')

            # 將board資料夾中的XML檔案轉成JSON檔案
            convert_xml_to_json(board_folder, json_folder, folder_name)

            # 處理JSON檔案並輸出到All_dataset資料夾
            match_questions_answers_comments(json_folder, output_file)

# 指定你的基礎資料夾和All_dataset資料夾
base_folder = '/home/hsin/DS_QA_Linebot/sally/專題/問答資料'
all_data_folder = '/home/hsin/DS_QA_Linebot/sally/專題/問答資料/All_dataset'
process_all_folders(base_folder, all_data_folder)
