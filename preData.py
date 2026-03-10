import pandas as pd
from sklearn.model_selection import train_test_split

# 1. 加载数据 (假设你的文件名为 data.csv，如果是从图片录入的，请确保已转为csv/excel)
# 如果是excel，使用 pd.read_excel('file.xlsx')
df = pd.read_csv('data.csv')

# 2. 标签映射
# 将 '正面' 映射为 1，'负面' 映射为 0
label_map = {'正面': 1, '负面': 0}
df['label'] = df['label'].map(label_map)

# 3. 第一次拆分：拆出 80% 的训练集，剩下 20% 用于验证+测试
train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['label'])

# 4. 第二次拆分：将剩下的 20% 平分为验证集和测试集 (各占总体的 10%)
val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['label'])

# 5. 保存为 CSV 格式
train_df.to_csv('train.csv', index=False, encoding='utf-8-sig')
val_df.to_csv('val.csv', index=False, encoding='utf-8-sig')
test_df.to_csv('test.csv', index=False, encoding='utf-8-sig')

print(f"处理完成：\n训练集: {len(train_df)} 条\n验证集: {len(val_df)} 条\n测试集: {len(test_df)} 条")