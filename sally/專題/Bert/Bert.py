from transformers import BertTokenizer, BertForQuestionAnswering
import torch

# 载入中文预训练的BERT模型和分词器
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = BertForQuestionAnswering.from_pretrained('bert-base-chinese')

# 定义问题和段落
question = "以自己的話描述遞迴recursion是什麼"
paragraph = (
    "遞迴是一種程式設計技術，其中一個函數呼叫它自己。這種技術通常用於解決問題的一部分，"
    "其中問題可以被分解成較小的相同類型的問題。每次遞迴呼叫都會進入下一層，直到達到基礎情況，"
    "此時不再進行遞迴。"
)

# 编码输入
inputs = tokenizer(question, paragraph, return_tensors='pt')

# 获取模型的输出
with torch.no_grad():
    outputs = model(**inputs)

# 获取答案的起始和结束位置
answer_start_index = torch.argmax(outputs.start_logits)
answer_end_index = torch.argmax(outputs.end_logits) + 1

# 解码答案
answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs['input_ids'][0][answer_start_index:answer_end_index]))

print(f"Question: {question}")
print(f"Answer: {answer}")
