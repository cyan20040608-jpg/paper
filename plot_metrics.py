import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. 设置风格：纯白背景，无网格
plt.style.use('seaborn-v0_8-white')

# 设置中文字体 (防止乱码)
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def smooth_curve(points, factor=0.85):
    """平滑曲线函数"""
    smoothed_points = []
    for point in points:
        if smoothed_points:
            previous = smoothed_points[-1]
            smoothed_points.append(previous * factor + point * (1 - factor))
        else:
            smoothed_points.append(point)
    return smoothed_points


def plot_separate_figures():
    # 文件配置
    files = [
        ('log_group_a_no_cnn.csv', 'Model A: No CNN', 'blue'),
        ('log_group_b_no_lora.csv', 'Model B: No LoRA', 'green'),
        ('log_group_c_full.csv', 'Model C: Full Model (Ours)', 'red')
    ]

    # 读取数据
    data = {}
    for filename, label, color in files:
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                data[label] = {'df': df, 'color': color}
                print(f"✅ 成功加载: {filename}")
            except Exception as e:
                print(f"❌ 读取错误 {filename}: {e}")
        else:
            print(f"⚠️ 文件不存在: {filename}")

    if not data:
        print("没有找到日志文件，无法绘图。")
        return

    # ==========================================
    # 图 1: 验证集 F1 Score (核心指标)
    # ==========================================
    plt.figure(figsize=(8, 6), dpi=300)  # 8x6英寸，300DPI高清
    for label, item in data.items():
        df = item['df']
        plt.plot(df['Step'], df['F1'], label=label, color=item['color'], linewidth=2.5, marker='.', markersize=8)

    plt.title('Validation F1 Score Comparison', fontsize=14, fontweight='bold')
    plt.xlabel('Global Steps', fontsize=12)
    plt.ylabel('F1 Score', fontsize=12)
    plt.legend(fontsize=10, loc='best')
    plt.tight_layout()
    plt.savefig('f1_score_comparison.png')
    print("🎉 F1对比图已保存: f1_score_comparison.png")
    plt.close()  # 关闭当前画布，防止重叠

    # ==========================================
    # 图 2: 验证集 Loss
    # ==========================================
    plt.figure(figsize=(8, 6), dpi=300)
    for label, item in data.items():
        df = item['df']
        plt.plot(df['Step'], df['Val_Loss'], label=label, color=item['color'], linewidth=2.5, linestyle='--')

    plt.title('Validation Loss Comparison', fontsize=14, fontweight='bold')
    plt.xlabel('Global Steps', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig('val_loss_comparison.png')
    print("🎉 验证Loss图已保存: val_loss_comparison.png")
    plt.close()

    # ==========================================
    # 图 3: 训练集 Loss (平滑后)
    # ==========================================
    plt.figure(figsize=(8, 6), dpi=300)
    for label, item in data.items():
        df = item['df']
        smoothed_loss = smooth_curve(df['Train_Loss'])
        plt.plot(df['Step'], smoothed_loss, label=label, color=item['color'], linewidth=2, alpha=0.9)

    plt.title('Training Loss Comparison (Smoothed)', fontsize=14, fontweight='bold')
    plt.xlabel('Global Steps', fontsize=12)
    plt.ylabel('Loss', fontsize=12)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig('train_loss_comparison.png')
    print("🎉 训练Loss图已保存: train_loss_comparison.png")
    plt.close()


if __name__ == '__main__':
    plot_separate_figures()