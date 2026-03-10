import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel, get_linear_schedule_with_warmup
from peft import get_peft_model, LoraConfig, TaskType
import pandas as pd
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
import os
import json
from torch.optim import AdamW


class Config:
    model_name = './bert-base-chinese'
    train_path = 'train.csv'
    val_path = 'val.csv'

    # [保存路径] A组：无 CNN
    save_path = './model_group_a_no_cnn'
    log_path = 'log_group_a_no_cnn.csv'

    max_len = 128
    batch_size = 32
    epochs = 2
    learning_rate = 1e-3
    save_steps = 500
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    lora_r = 8
    lora_alpha = 16
    lora_dropout = 0.1
    num_labels = 2


def save_config_to_json(config_class, output_path):
    config_dict = {k: v for k, v in config_class.__dict__.items() if not k.startswith('__')}
    config_dict['device'] = str(config_dict['device'])
    json_path = os.path.join(output_path, 'config.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=4, ensure_ascii=False)


class SentimentDataset(Dataset):
    def __init__(self, filename, tokenizer, max_len):
        self.df = pd.read_csv(filename)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self): return len(self.df)

    def __getitem__(self, index):
        text = str(self.df.loc[index, 'sentence'])
        label = int(self.df.loc[index, 'label'])
        encoding = self.tokenizer.encode_plus(text, add_special_tokens=True, max_length=self.max_len,
                                              padding='max_length', truncation=True, return_tensors='pt')
        return {'input_ids': encoding['input_ids'].flatten(), 'attention_mask': encoding['attention_mask'].flatten(),
                'labels': torch.tensor(label, dtype=torch.long)}


# === 模型变化：无 CNN ===
class BertLoRALinear(nn.Module):
    def __init__(self, config):
        super(BertLoRALinear, self).__init__()
        base_bert = BertModel.from_pretrained(config.model_name)
        peft_config = LoraConfig(task_type=TaskType.FEATURE_EXTRACTION, inference_mode=False, r=config.lora_r,
                                 lora_alpha=config.lora_alpha, lora_dropout=config.lora_dropout,
                                 target_modules=["query", "value"])
        self.bert = get_peft_model(base_bert, peft_config)
        self.dropout = nn.Dropout(0.3)
        # 直接接全连接层
        self.fc = nn.Linear(768, config.num_labels)

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.bert(input_ids, attention_mask=attention_mask)
        # 取 [CLS]
        cls_output = outputs.last_hidden_state[:, 0, :]
        logits = self.fc(self.dropout(cls_output))
        loss = nn.CrossEntropyLoss()(logits, labels) if labels is not None else None
        return loss, logits


def eval_model(model, loader):
    model.eval()
    preds, labels, losses = [], [], []
    with torch.no_grad():
        for batch in loader:
            input_ids = batch['input_ids'].to(Config.device)
            mask = batch['attention_mask'].to(Config.device)
            label = batch['labels'].to(Config.device)
            loss, logits = model(input_ids, mask, label)
            losses.append(loss.item())
            preds.extend(torch.max(logits, 1)[1].cpu().numpy())
            labels.extend(label.cpu().numpy())
    p, r, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    return np.mean(losses), f1


if __name__ == '__main__':
    if not os.path.exists(Config.save_path): os.makedirs(Config.save_path)
    tokenizer = BertTokenizer.from_pretrained(Config.model_name)
    train_loader = DataLoader(SentimentDataset(Config.train_path, tokenizer, Config.max_len),
                              batch_size=Config.batch_size, shuffle=True)
    val_loader = DataLoader(SentimentDataset(Config.val_path, tokenizer, Config.max_len), batch_size=Config.batch_size)

    print(">>> A组: LoRA + Linear (无CNN) 启动 <<<")
    model = BertLoRALinear(Config).to(Config.device)
    optimizer = AdamW(model.parameters(), lr=Config.learning_rate)
    scheduler = get_linear_schedule_with_warmup(optimizer, 0, len(train_loader) * Config.epochs)

    best_f1, global_step, history = 0, 0, []
    for epoch in range(Config.epochs):
        model.train()
        train_losses = []
        for batch in train_loader:
            loss, _ = model(batch['input_ids'].to(Config.device), batch['attention_mask'].to(Config.device),
                            batch['labels'].to(Config.device))
            train_losses.append(loss.item())
            loss.backward()
            optimizer.step();
            scheduler.step();
            optimizer.zero_grad()
            global_step += 1

            if global_step % Config.save_steps == 0:
                val_loss, f1 = eval_model(model, val_loader)
                print(f"Step {global_step} | Val Loss: {val_loss:.4f} | F1: {f1:.4f}")
                history.append(
                    {'Epoch': epoch + 1, 'Step': global_step, 'Train_Loss': np.mean(train_losses), 'Val_Loss': val_loss,
                     'F1': f1})
                pd.DataFrame(history).to_csv(Config.log_path, index=False)
                train_losses = []

                if f1 > best_f1:
                    best_f1 = f1
                    torch.save(model.state_dict(), os.path.join(Config.save_path, 'best_model.bin'))
                    save_config_to_json(Config, Config.save_path)
                    print(f"🌟 新高分 (F1: {f1:.4f})，已保存！")
                model.train()
    print(f"\n训练结束！最高 F1: {best_f1:.4f}")