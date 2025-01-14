import json
import pandas as pd
from sklearn.metrics import confusion_matrix

# 讀取資料
with open('abc_format.json', 'r', encoding='utf-8') as f:
    test_data = json.load(f)

with open('abc_format_result.json', 'r', encoding='utf-8') as f:
    model_output = json.load(f)
    
# 提取分數
y_true = []
y_pred = []

# 計數原始和新分數的0-1、2-3數量
count_true = {"0-1": 0, "2-3": 0}
count_pred = {"0-1": 0, "2-3": 0}

# 無效分數和範圍外分數的計數
invalid_true_count = 0
invalid_pred_count = 0
out_of_range_true_count = 0  # 真實分數不在0-3範圍內
out_of_range_pred_count = 0  # 預測分數不在0-3範圍內

# 處理分數的函數，將 0 和 1 合併為 "0-1"，2 和 3 合併為 "2-3"
def process_score(score, invalid_count_name, out_of_range_count_name, count_dict):
    global invalid_true_count, invalid_pred_count, out_of_range_true_count, out_of_range_pred_count
    
    if score in [None, ""]:  # 處理空字串或 None 的情況
        if invalid_count_name == 'true':
            invalid_true_count += 1
        else:
            invalid_pred_count += 1
        return "0-1"
    elif isinstance(score, str) and score.isdigit():
        score_int = int(score)
        if score_int < 0 or score_int > 3:  # 調整範圍至 0-3
            if out_of_range_count_name == 'true':
                out_of_range_true_count += 1
            else:
                out_of_range_pred_count += 1
        # 將 0 和 1 合併為 "0-1"，2 和 3 合併為 "2-3"
        if score_int >= 2:
            score_label = "2-3"
        else:
            score_label = "0-1"
        if score_label in count_dict:  # 計數 "0-1", "2-3" 分
            count_dict[score_label] += 1
        return score_label
    return "0-1"

# 遍歷每個測試項目和模型輸出
for test_item, model_item in zip(test_data, model_output):
    y_true.append(process_score(test_item['score'], 'true', 'true', count_true))
    y_pred.append(process_score(model_item['score'], 'pred', 'pred', count_pred))

# 確保 y_true 和 y_pred 長度一致
if len(y_true) != len(y_pred):
    raise ValueError("兩個檔案中的分數數量不一致。")

# 計算每個標籤的 TP, FP, FN, Precision, Recall, F1
def calculate_metrics(y_true, y_pred, label):
    TP = sum(1 for true, pred in zip(y_true, y_pred) if true == label and pred == label)
    FP = sum(1 for true, pred in zip(y_true, y_pred) if true != label and pred == label)
    FN = sum(1 for true, pred in zip(y_true, y_pred) if true == label and pred != label)
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return {'TP': TP, 'FP': FP, 'FN': FN, 'Precision': precision, 'Recall': recall, 'F1': f1}

# 取得所有標籤（包括 0 分）合併後的分數
labels = sorted(set(y_true), key=lambda x: str(x))

# 計算每個分數的指標
metrics = {}
for label in labels:
    metrics[label] = calculate_metrics(y_true, y_pred, label)

# 輸出原始數據中的分數數量
print("原始數據中的分數數量：")
print(f"  0-1 分: {count_true['0-1']}")
print(f"  2-3 分: {count_true['2-3']}")

print("模型預測數據中的分數數量：")
print(f"  0-1 分: {count_pred['0-1']}")
print(f"  2-3 分: {count_pred['2-3']}")

# 輸出無效和範圍外的計數
print(f"無效的真實分數: {invalid_true_count}, 無效的預測分數: {invalid_pred_count}")
print(f"範圍外的真實分數: {out_of_range_true_count}, 範圍外的預測分數: {out_of_range_pred_count}")

# 計算混淆矩陣（合併後的分數）
conf_matrix = confusion_matrix(y_true, y_pred, labels=["0-1", "2-3"])

# 使用 pandas 顯示混淆矩陣表格
conf_matrix_df = pd.DataFrame(conf_matrix, index=[f"True {i}" for i in ["0-1", "2-3"]],
                              columns=[f"Pred {i}" for i in ["0-1", "2-3"]])

print("\n混淆矩陣：")
print(conf_matrix_df)

# 輸出每個分數的結果
for label in labels:
    metric = metrics[label]
    print(f"Score {label}:")
    print(f"  TP: {metric['TP']}, FP: {metric['FP']}, FN: {metric['FN']}")
    print(f"  Precision: {metric['Precision']:.2f}, Recall: {metric['Recall']:.2f}, F1: {metric['F1']:.2f}")

# 計算加權平均 F1 分數
f1_weighted = sum(metric['F1'] for metric in metrics.values()) / len(metrics)
print(f"加權平均 F1 分數: {f1_weighted:.2f}")
