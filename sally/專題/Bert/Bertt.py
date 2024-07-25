import torch
from transformers import BertForQuestionAnswering, BertTokenizer

def answer_question(question):
    # 載入BERT模型和tokenizer
    model_name = "bert-base-uncased"
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForQuestionAnswering.from_pretrained(model_name)

    # 將問題轉換為tokens
    inputs = tokenizer.encode_plus(question, return_tensors="pt", add_special_tokens=True)

    # 使用BERT模型預測答案的開始和結束位置
    start_scores, end_scores = model(**inputs).values()

    # 從預測的起始和結束位置中找出最高分的答案
    answer_start = torch.argmax(start_scores)
    answer_end = torch.argmax(end_scores)

    # 將token轉換回文字
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end+1]))

    return answer

# 測試
question = "1+5"
answer = answer_question(question)
print("Answer:", answer)
