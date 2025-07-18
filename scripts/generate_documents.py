import json
import os
import csv

# 設定來源資料路徑（清理後的食譜）
INPUT_JSON_PATH = os.path.join("..", "cleaned_csv", "小白菜_清理後食譜.json")

# 設定輸出路徑
OUTPUT_CSV_PATH = os.path.join("..", "cleaned_csv", "recipe_documents.csv")

def load_recipes(json_path):
    """載入清理後的 JSON 食譜資料"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_documents(recipes):
    """將每個食譜的食材名稱組合成一行字串"""
    documents = []
    for recipe in recipes:
        recipe_id = recipe.get("id", "")
        structured_ingredients = recipe.get("structured_ingredients", [])
        # 抽出每個食材名稱
        ingredient_names = [ingredient.get("name", "") for ingredient in structured_ingredients]
        # 合併成一行文字
        document = " ".join(ingredient_names)
        documents.append({
            "id": recipe_id,
            "document": document
        })
    return documents

def save_documents_to_csv(documents, output_path):
    """將食譜文件輸出成 CSV 檔"""
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "document"])
        writer.writeheader()
        writer.writerows(documents)

def main():
    recipes = load_recipes(INPUT_JSON_PATH)
    documents = generate_documents(recipes)
    save_documents_to_csv(documents, OUTPUT_CSV_PATH)
    print(f"✅ 已產生 {len(documents)} 筆食譜文件，儲存於：{OUTPUT_CSV_PATH}")

if __name__ == "__main__":
    main()
