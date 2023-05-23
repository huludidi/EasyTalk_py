import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 加载预训练的文本分类模型
model_name = 'bert-base-chinese'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# 定义敏感词汇和不良内容
sensitive_words = ['cao', '操', '艹','我操了', '卧槽了', '你妹的']
inappropriate_content = ['我操了', '卧槽了', '你妹的']


def textAudit(text, threshold=0.6):
    sensitive_and_inappropriate_words = ['cao', '操', '艹', '我操了', '卧槽了', '你妹的']

    # 使用预训练的文本分类模型对文本进行分类
    with torch.no_grad():
        inputs = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
        inputs.to(device)
        outputs = model(**inputs)
        logits = outputs.logits.detach().cpu().numpy()[0]
        prediction_score = float(logits[1])

    # 判断文本是否属于违规文本，并返回审核结果
    if prediction_score > threshold or any(word in text for word in sensitive_and_inappropriate_words):
        return False
    return True