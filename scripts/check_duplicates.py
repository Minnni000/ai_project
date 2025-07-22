import os
import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def analyze_recipe_similarity(input_csv_path, output_csv_path, threshold=0.5):
    """
    分析食譜相似度並輸出結果到 CSV 檔案
    """
    # 讀取 CSV
    df = pd.read_csv(input_csv_path)

    if len(df) < 2:
        print(f"⚠️  檔案 {input_csv_path} 中的食譜數量少於 2 筆，無法進行相似度分析")
        return

    # TF-IDF 向量化
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df["document"])

    # 計算相似度矩陣（NxN）
    cosine_sim = cosine_similarity(tfidf_matrix)

    print(f"📊 分析所有食譜組合的相似度...")

    # 收集所有相似度數值（包含低於門檻的）
    all_similarities = []
    for i in range(len(df)):
        for j in range(i+1, len(df)):
            sim_score = cosine_sim[i][j]
            id1 = df.iloc[i]["id"]
            name1 = df.iloc[i]["name"]
            id2 = df.iloc[j]["id"]
            name2 = df.iloc[j]["name"]

            all_similarities.append({
                "食譜1_ID": id1,
                "食譜1_名稱": name1,
                "食譜2_ID": id2,
                "食譜2_名稱": name2,
                "相似度": round(sim_score, 3)
            })

    # 按相似度排序（從高到低）
    all_similarities.sort(key=lambda x: x["相似度"], reverse=True)

    # 分析不同門檻下的結果
    thresholds = [0.1, 0.2, 0.3, 0.4, 0.5]
    threshold_analysis = []
    for test_threshold in thresholds:
        count = sum(1 for sim in all_similarities if sim['相似度'] > test_threshold)
        threshold_analysis.append({
            "門檻": test_threshold,
            "相似食譜組數": count
        })

    # 計算建議門檻和統計資訊
    analysis_summary = {}
    if all_similarities:
        max_sim = all_similarities[0]['相似度']
        suggested_threshold = max(0.1, max_sim * 0.8)  # 最高相似度的 80%
        analysis_summary = {
            "最高相似度": max_sim,
            "建議門檻": round(suggested_threshold, 2),
            "總食譜組合數": len(all_similarities),
            "分析門檻": threshold,
            "符合門檻的組合數": len([sim for sim in all_similarities if sim['相似度'] > threshold])
        }

    # 顯示高於當前門檻的結果
    similarity_results = [sim for sim in all_similarities if sim['相似度'] > threshold]

    # 儲存結果到 CSV（保持原本格式）
    if similarity_results:
        result_df = pd.DataFrame(similarity_results)
        # 按相似度排序（從高到低）
        result_df = result_df.sort_values('相似度', ascending=False)

        # 在 CSV 檔案中添加分析資訊作為註解行
        with open(output_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            # 寫入分析資訊作為註解
            if analysis_summary:
                f.write(f"# 分析摘要\n")
                f.write(f"# 最高相似度: {analysis_summary['最高相似度']:.3f}\n")
                f.write(f"# 建議門檻: {analysis_summary['建議門檻']:.2f} (最高相似度的80%)\n")
                f.write(f"# 總食譜組合數: {analysis_summary['總食譜組合數']}\n")
                f.write(f"# 當前分析門檻: {analysis_summary['分析門檻']}\n")
                f.write(f"# 符合門檻組合數: {analysis_summary['符合門檻的組合數']}\n")
                f.write(f"#\n")

            # 寫入門檻分析
            f.write(f"# 不同門檻下的相似食譜數量\n")
            for item in threshold_analysis:
                f.write(f"# 門檻 {item['門檻']}: {item['相似食譜組數']} 組相似食譜\n")
            f.write(f"#\n")
            f.write(f"# 相似度結果 (高於 {threshold})\n")

            # 寫入正常的 CSV 資料
            result_df.to_csv(f, index=False)

        print(f"✅ 找到 {len(similarity_results)} 組相似食譜，結果已儲存到：{output_csv_path}")
    else:
        # 即使沒有相似食譜，也建立包含分析資訊的 CSV 檔案
        with open(output_csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            # 寫入分析資訊
            if analysis_summary:
                f.write(f"# 分析摘要\n")
                f.write(f"# 最高相似度: {analysis_summary['最高相似度']:.3f}\n")
                f.write(f"# 建議門檻: {analysis_summary['建議門檻']:.2f} (最高相似度的80%)\n")
                f.write(f"# 總食譜組合數: {analysis_summary['總食譜組合數']}\n")
                f.write(f"# 當前分析門檻: {analysis_summary['分析門檻']}\n")
                f.write(f"# 符合門檻組合數: {analysis_summary['符合門檻的組合數']}\n")
                f.write(f"#\n")

            # 寫入門檻分析
            f.write(f"# 不同門檻下的相似食譜數量\n")
            for item in threshold_analysis:
                f.write(f"# 門檻 {item['門檻']}: {item['相似食譜組數']} 組相似食譜\n")
            f.write(f"#\n")
            f.write(f"# 沒有找到相似度高於 {threshold} 的食譜組合\n")

            # 寫入空的 CSV 標題
            empty_df = pd.DataFrame(columns=["食譜1_ID", "食譜1_名稱", "食譜2_ID", "食譜2_名稱", "相似度"])
            empty_df.to_csv(f, index=False)

        print(f"ℹ️  沒有找到相似度高於 {threshold} 的食譜組合，已建立包含分析資訊的結果檔案：{output_csv_path}")


def main():
    # 取得腳本所在目錄和專案根目錄
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))
    cleaned_csv_dir = os.path.join(project_root, "cleaned_csv")

    # 設定相似度門檻
    threshold = 0.3

    if not os.path.exists(cleaned_csv_dir):
        print(f"❌ 找不到 cleaned_csv 目錄：{cleaned_csv_dir}")
        sys.exit(1)

    # 尋找所有菜名資料夾
    vegetable_dirs = [d for d in os.listdir(cleaned_csv_dir)
                     if os.path.isdir(os.path.join(cleaned_csv_dir, d))]

    if not vegetable_dirs:
        print("❌ 在 cleaned_csv 目錄中找不到任何菜名資料夾")
        sys.exit(1)

    print(f"🔍 找到 {len(vegetable_dirs)} 個菜名資料夾：{', '.join(vegetable_dirs)}")
    print(f"📈 相似度門檻設定為：{threshold}")
    print("=" * 60)

    # 處理每個菜名資料夾
    for vegetable_name in vegetable_dirs:
        vegetable_dir = os.path.join(cleaned_csv_dir, vegetable_name)

        # 設定輸入和輸出檔案路徑
        input_csv_path = os.path.join(vegetable_dir, f"{vegetable_name}_recipe_documents.csv")
        output_csv_path = os.path.join(vegetable_dir, f"{vegetable_name}_食譜相似度分析.csv")

        print(f"\n🥬 處理菜名：{vegetable_name}")

        if not os.path.exists(input_csv_path):
            print(f"⚠️  找不到檔案：{os.path.basename(input_csv_path)}，跳過此菜名")
            continue

        # 執行相似度分析
        analyze_recipe_similarity(input_csv_path, output_csv_path, threshold)

    print("\n🎉 所有菜名的相似度分析完成！")


if __name__ == "__main__":
    main()

