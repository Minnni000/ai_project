# 🍳 AI Recipe Project - 智慧食譜分析系統

一個基於機器學習的食譜資料處理與分析系統，提供食譜爬取、資料清理、向量化分析、相似度比對等功能。

## 📋 目錄結構

```
ai_project/
├── cleaned_csv/           # 清理後的食譜資料
│   ├── 小白菜/
│   ├── 九層塔/
│   ├── 牛番茄/
│   └── ...
├── database/             # 結構化資料庫
│   ├── extracted_ingredients.csv
│   ├── ingredient_database.csv
│   └── main_recipe_database.csv
├── image/               # 食譜圖片
│   ├── all_pic/        # 統一命名的圖片
│   ├── 小白菜/
│   └── ...
├── raw_csv/            # 原始爬取資料
├── scripts/            # 核心處理腳本
└── models/             # 訓練模型存放
```

## 🚀 快速開始

### 環境需求
```bash
pip install pandas numpy scikit-learn beautifulsoup4 requests
```

### 完整流水線執行
```bash
# 執行完整處理流程
python scripts/run_pipeline.py

# 指定蔬菜名稱
python scripts/run_pipeline.py 小白菜

# 從特定步驟開始
python scripts/run_pipeline.py --start-from clean
```

## 🛠️ 核心功能

### 1. 資料爬取
- **腳本**: `crawl_icook_recipes.py`
- **功能**: 從 iCook 網站爬取食譜資料
- **輸出**: `raw_csv/{蔬菜名}_食譜資料.csv`

```bash
python scripts/crawl_icook_recipes.py 小白菜
```

### 2. 資料清理
- **腳本**: `clean_recipe_csv_0720.py`
- **功能**: 清理食材格式、解析結構化資料
- **輸出**: `cleaned_csv/{蔬菜名}/{蔬菜名}_清理後食譜.json`

```bash
python scripts/clean_recipe_csv_0720.py --all
```

### 3. 向量化處理
- **腳本**: `generate_documents.py`
- **功能**: 生成 TF-IDF 向量化文件
- **輸出**: `cleaned_csv/{蔬菜名}/recipe_documents.csv`

```bash
python scripts/generate_documents.py --all
```

### 4. 相似度分析
- **腳本**: `check_duplicates.py`
- **功能**: 分析食譜相似度，找出重複或相似食譜
- **輸出**: `cleaned_csv/{蔬菜名}/{蔬菜名}_食譜相似度分析.csv`

```bash
python scripts/check_duplicates.py
```

## 📊 資料庫工具

### 建立資料庫
```bash
# 建立主食譜資料庫
python scripts/create_database.py

# 建立食材資料庫
python scripts/create_database.py ingredient

# 建立食譜步驟資料庫
python scripts/create_database.py steps
```

### 食材提取
```bash
# 從 JSON 檔案提取食材資料
python scripts/extract_ingredients_from_json.py
```

## 🖼️ 圖片處理

### 統一圖片命名
```bash
# 將所有圖片重新命名為 ID.jpg 格式並複製到 all_pic 資料夾
python scripts/pic_id.py
```

## 🗑️ 資料管理

### 刪除食譜
1. 在 `scripts/delete_list.txt` 中列出要刪除的食譜 ID
2. 執行刪除腳本：
```bash
python scripts/delete_recipe.py
```

## 📈 分析結果

### 相似度分析報告
每個蔬菜資料夾會生成相似度分析報告，包含：
- 最高相似度統計
- 建議門檻值
- 相似食譜配對清單
- 不同門檻下的統計數據

### 資料庫輸出
- **主食譜資料庫**: 包含基本食譜資訊
- **食材資料庫**: 詳細食材清單與用量
- **食譜步驟資料庫**: 完整製作步驟

## 🔧 進階功能

### 自訂處理
- 修改 `clean_recipe_csv_0720.py` 中的清理規則
- 調整 `check_duplicates.py` 中的相似度門檻
- 擴展 `crawl_icook_recipes.py` 支援更多網站

### 模型訓練
- TF-IDF 向量化模型
- 食譜分類模型
- 相似度計算模型

## 📝 資料格式

### 原始資料 (raw_csv)
```csv
id,食譜名稱,網址,預覽食材,詳細食材,做法,圖片相對路徑
```

### 清理後資料 (JSON)
```json
{
  "id": "479305",
  "name": "大蒜油",
  "url": "https://icook.tw/recipes/479305",
  "preview_ingredients": "去皮大蒜、沙拉油、食鹽",
  "ingredients": ["去皮大蒜100g", "沙拉油150g"],
  "structured_ingredients": [
    {"name": "去皮大蒜", "quantity": 100.0, "unit": "g"}
  ],
  "steps": ["步驟1", "步驟2"],
  "image_path": "蒜頭/479305.jpg"
}
```

