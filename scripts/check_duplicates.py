import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 取得目前腳本所在路徑
base_dir = os.path.dirname(__file__)

# 使用相對路徑取得資料檔案位置
csv_path = os.path.join(base_dir, '..', 'cleaned_csv', 'recipe_documents.csv')

# 讀取 CSV
df = pd.read_csv(csv_path)

# TF-IDF 向量化
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df["document"])

# 計算相似度矩陣（NxN）
cosine_sim = cosine_similarity(tfidf_matrix)

# 設定相似度門檻
threshold = 0.5

print("以下是相似度高於", threshold, "的食譜組合：\n")

# 比對每一對食譜
for i in range(len(df)):
    for j in range(i+1, len(df)):
        sim_score = cosine_sim[i][j]
        if sim_score > threshold:
            id1 = df.iloc[i]["id"]
            name1 = df.iloc[i]["name"]
            id2 = df.iloc[j]["id"]
            name2 = df.iloc[j]["name"]
            print(f"{id1}（{name1}） 與 {id2}（{name2}） 的相似度 = {sim_score:.3f}")

