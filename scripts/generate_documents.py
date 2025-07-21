import json
import os
import csv
import re

# 設定來源資料路徑（清理後的食譜）
INPUT_JSON_PATH = os.path.join("..", "cleaned_csv", "小白菜_清理後食譜.json")

# 設定輸出路徑
OUTPUT_CSV_PATH = os.path.join("..", "cleaned_csv", "recipe_documents.csv")

# 定義要移除的食材（通用調味料／媒介物）
REMOVE_INGREDIENTS = set([
    # 鹽類
    "鹽", "鹽巴", "鹽吧", "食用鹽",
    "精鹽", "粗鹽", "海鹽", "岩鹽", "玫瑰鹽", "湖鹽",
    "黑鹽", "喜馬拉雅鹽", "夏威夷鹽", "日式鹽", "天日鹽",
    "胡椒鹽", "蒜味鹽", "檸檬鹽", "香料鹽", "昆布鹽",
    # 油類
    "油", "食用油",
    "豬油", "牛油", "雞油", "鴨油", "魚油",
    "芥花油", "橄欖油", "花生油", "大豆油", "玉米油", "葵花油", "棕櫚油", "椰子油",
    "亞麻仁油", "酪梨油", "葡萄籽油", "苦茶油",
    "沙拉油", "炸油", "調和油",
    # 水類
    "水", "飲用水", "開水",
    "高湯", "水煮", "冷水", "熱水", "冰水",
    "礦泉水", "純水", "蒸餾水",
    "米水", "蔬菜水", "泡菜水", "浸泡水"
])


def load_recipes(json_path):
    """載入清理後的 JSON 食譜資料"""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def clean_ingredient_text(text: str) -> list[str]:
    """
    將原始 ingredient 字串轉為乾淨的食材名稱列表。
    """
    # 將常見分隔符（頓號、斜線、逗號）換成空白
    text = re.sub(r"[、/,，]", " ", text)
    # 移除 emoji、特殊符號，只保留中英文與數字與空白
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s]", "", text)
    # 分詞並去除空白項
    parts = [part.strip() for part in text.split() if part.strip()]
    # 過濾不需要的食材（轉為 set 加速）
    parts = [p for p in parts if p not in REMOVE_INGREDIENTS]
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
        documents.append({"id": recipe_id, "name": recipe["name"], "document": document})
    return documents


def save_documents_to_csv(documents, output_path):
    """將食譜文件輸出成 CSV 檔"""
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "document"])
        writer.writeheader()
        writer.writerows(documents)


def main():
    recipes = load_recipes(INPUT_JSON_PATH)
    documents = generate_documents(recipes)
    save_documents_to_csv(documents, OUTPUT_CSV_PATH)
    print(f"✅ 已產生 {len(documents)} 筆食譜文件，儲存於：{OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()
