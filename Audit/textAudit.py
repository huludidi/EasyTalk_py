# import torch
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
#
# # 加载预训练的文本分类模型
# model_name = 'bert-base-chinese'
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# model.to(device)
#
# # 定义敏感词汇和不良内容
# sensitive_words = ['cao', '操', '艹','我操了', '卧槽了', '你妹的']
# inappropriate_content = ['我操了', '卧槽了', '你妹的']
#
#
# def textAudit(text, threshold=0.6):
#     sensitive_and_inappropriate_words = ['cao', '操', '艹', '我操了', '卧槽了', '你妹的']
#
#     # 使用预训练的文本分类模型对文本进行分类
#     with torch.no_grad():
#         inputs = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
#         inputs.to(device)
#         outputs = model(**inputs)
#         logits = outputs.logits.detach().cpu().numpy()[0]
#         prediction_score = float(logits[1])
#
#     # 判断文本是否属于违规文本，并返回审核结果
#     if prediction_score > threshold or any(word in text for word in sensitive_and_inappropriate_words):
#         return False
#     return True

import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 加载预训练的文本分类模型
model_name = 'yechen/bert-large-chinese'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# 定义敏感词汇列表、阈值和正则表达式
sensitive_words = ['操', '草', '干', '艹', '我操了', '卧槽了', '你妹的']
inappropriate_content = ['我操了', '卧槽了', '你妹的']
threshold = 0.8
pattern = re.compile('[\u4e00-\u9fa5]')

def textAudit(text):
    # 使用正则表达式清洗输入文本
    text = pattern.findall(text)
    text = ''.join(text)
    text = text.strip()

    # 判断文本是否包含敏感词汇
    for word in sensitive_words:
        if word in text:
            return False

    # 使用预训练的文本分类模型对文本进行分类
    with torch.no_grad():
        inputs = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
        inputs.to(device)
        outputs = model(**inputs)
        logits = outputs.logits.detach().cpu().numpy()[0]
        prediction_score = float(logits[1])

    # 判断文本是否属于不良内容，判定为违规文本，并返回审核结果
    if prediction_score > threshold or any(word in text for word in inappropriate_content):
        return False
    return True