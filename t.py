import matplotlib.pyplot as plt

# 設定 font.sans-serif 為 SimHei，讓 matplotlib 使用該字體
plt.rcParams['font.sans-serif'] = ['SimHei']  # 指定使用 SimHei 字體
plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示為方框的問題

# 測試繪圖
plt.plot([1, 2, 3], [4, 5, 6])
plt.title('測試中文標題')
plt.xlabel('X 軸')
plt.ylabel('Y 軸')
plt.savefig('output.png')  # 保存圖表
