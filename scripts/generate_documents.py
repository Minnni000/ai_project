import json
import os
import csv

# 設定來源資料路徑（清理後的食譜）
INPUT_JSON_PATH = os.path.join("..", "cleaned_csv", "小白菜_清理後食譜.json")

# 設定輸出路徑
OUTPUT_CSV_PATH = os.path.join("..", "cleaned_csv", "recipe_documents.csv")


def load_recipes(json_path):
    """載入清理後的 JSON 食譜資料"""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


import re


def clean_ingredient_text(text: str) -> list[str]:
    """
    將原始 ingredient 字串轉為乾淨的食材名稱列表。
    範例："韭菜* /蒜頭🧄/辣椒🌶️" => ["韭菜", "蒜頭", "辣椒"]
    """
    # 將常見分隔符（頓號、斜線、逗號）統一換成空白
    text = re.sub(r"[、/,，]", " ", text)

    # 移除 emoji、特殊符號，只保留中英文與數字（含空白）
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s]", "", text)

    # 分詞並去除空白項
    parts = [part.strip() for part in text.split() if part.strip()]
    return parts


def generate_documents(recipes: list[dict]) -> list[dict]:
    documents = []
    for recipe in recipes:
        recipe_id = recipe.get("id", "")
        preview_ingredients = recipe.get("preview_ingredients", [])

        ingredient_names: list[str] = []

        if isinstance(preview_ingredients, str):
            ingredient_names = clean_ingredient_text(preview_ingredients)

        elif isinstance(preview_ingredients, list):
            for ing in preview_ingredients:
                if isinstance(ing, dict):
                    name = ing.get("name", "").strip()
                    if name:
                        ingredient_names.extend(clean_ingredient_text(name))
                elif isinstance(ing, str):
                    ingredient_names.extend(clean_ingredient_text(ing))

        document = " ".join(ingredient_names)
        documents.append({"id": recipe_id, "document": document})
    return documents


def save_documents_to_csv(documents, output_path):
    """將食譜文件輸出成 CSV 檔"""
    with open(output_path, "w", encoding="utf-8", newline="") as f:
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
