import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 顯示當前工作路徑
current_dir = os.getcwd()
print("📂 現在執行位置：", current_dir)

# 相對路徑設定
csv_path = "../cleaned_csv/recipe_documents.csv"

# 檔案存在檢查
if not os.path.exists(csv_path):
    raise FileNotFoundError(f"❌ 找不到檔案：{csv_path}")

# 讀取資料
df = pd.read_csv(csv_path, encoding="utf-8")

# 建立搜尋語料（使用 combined_text 欄位）
corpus = df["combined_text"].fillna("").tolist()

# TF-IDF 向量化
vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
X = vectorizer.fit_transform(corpus)


# 搜尋函式
def search_recipe(query: str, top_k: int = 3):
    query_vec = vectorizer.transform([query])
    sim_scores = cosine_similarity(query_vec, X).flatten()
    top_indices = sim_scores.argsort()[::-1][:top_k]
    return df.iloc[top_indices][["name", "ingredients", "steps", "url", "image_path"]]


# 測試查詢：「小白菜 吻仔魚」
results = search_recipe("香菇 辣椒 小白菜", top_k=3)

# 顯示結果
for i, row in results.iterrows():
    print(f"📌 食譜名稱：{row['name']}")
    print(f"🧂 食材：{row['ingredients']}")
    print(f"🥢 步驟：{row['steps']}")
    print(f"🔗 網址：{row['url']}")
    print(f"🖼️ 圖片：{row['image_path']}")
    print("-" * 40)
