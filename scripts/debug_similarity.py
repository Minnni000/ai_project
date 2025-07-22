#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試相似度分析 - 顯示所有食譜之間的相似度數值
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

def debug_similarity():
    # 讀取小白菜的 recipe_documents.csv
    csv_path = os.path.join("..", "cleaned_csv", "小白菜", "小白菜_recipe_documents.csv")
    
    if not os.path.exists(csv_path):
        print(f"❌ 找不到檔案：{csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    print(f"📊 讀取到 {len(df)} 筆食譜")
    print("\n食譜清單：")
    for i, row in df.iterrows():
        print(f"  {i+1}. {row['name']} - {row['document']}")
    
    if len(df) < 2:
        print("⚠️  食譜數量少於 2 筆，無法計算相似度")
        return
    
    # TF-IDF 向量化
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df["document"])
    
    # 計算相似度矩陣
    cosine_sim = cosine_similarity(tfidf_matrix)
    
    print(f"\n📈 所有食譜之間的相似度（共 {len(df)} x {len(df)} 矩陣）：")
    print("=" * 80)
    
    # 顯示所有相似度組合
    all_similarities = []
    for i in range(len(df)):
        for j in range(i+1, len(df)):
            sim_score = cosine_sim[i][j]
            all_similarities.append({
                'recipe1': df.iloc[i]['name'],
                'recipe2': df.iloc[j]['name'],
                'similarity': sim_score
            })
            print(f"{i+1} vs {j+1}: {sim_score:.4f} - {df.iloc[i]['name']} vs {df.iloc[j]['name']}")
    
    # 排序並顯示最高相似度
    all_similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    print(f"\n🏆 相似度排行榜（從高到低）：")
    print("-" * 80)
    for i, sim in enumerate(all_similarities, 1):
        print(f"{i}. {sim['similarity']:.4f} - {sim['recipe1']} vs {sim['recipe2']}")
    
    # 分析不同門檻下的結果
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]
    print(f"\n📊 不同門檻下的相似食譜數量：")
    print("-" * 40)
    for threshold in thresholds:
        count = sum(1 for sim in all_similarities if sim['similarity'] > threshold)
        print(f"門檻 {threshold}: {count} 組相似食譜")
    
    # 建議最佳門檻
    if all_similarities:
        max_sim = all_similarities[0]['similarity']
        suggested_threshold = max(0.1, max_sim * 0.8)  # 最高相似度的 80%
        print(f"\n💡 建議門檻：{suggested_threshold:.2f} （最高相似度 {max_sim:.4f} 的 80%）")

if __name__ == "__main__":
    debug_similarity()
