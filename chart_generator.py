import matplotlib.pyplot as plt
import io

def generate_score_chart(unit_name, score_distribution):
    # score_distribution 是一個字典，鍵是分數，值是對應的題數
    scores = list(score_distribution.keys())
    counts = list(score_distribution.values())

    plt.figure(figsize=(10, 6))
    plt.bar(scores, counts, color='blue')
    plt.xlabel('分數')
    plt.ylabel('題數')
    plt.title(f'{unit_name} 分數分布')

    # 將圖表保存到內存中
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return buf
