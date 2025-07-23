import os
import csv
import re
import sys

# 定義要移除的食材（通用調味料／媒介物）
REMOVE_INGREDIENTS = set(
    [
        # 鹽類
        "鹽",
        "鹽巴",
        "鹽吧",
        "食用鹽",
        "精鹽",
        "粗鹽",
        "海鹽",
        "岩鹽",
        "玫瑰鹽",
        "湖鹽",
        "黑鹽",
        "喜馬拉雅鹽",
        "夏威夷鹽",
        "日式鹽",
        "天日鹽",
        "胡椒鹽",
        "蒜味鹽",
        "檸檬鹽",
        "香料鹽",
        "昆布鹽",
        # 油類
        "油",
        "食用油",
        "豬油",
        "牛油",
        "雞油",
        "鴨油",
        "魚油",
        "芥花油",
        "橄欖油",
        "花生油",
        "大豆油",
        "玉米油",
        "葵花油",
        "棕櫚油",
        "椰子油",
        "亞麻仁油",
        "酪梨油",
        "葡萄籽油",
        "苦茶油",
        "沙拉油",
        "炸油",
        "調和油" "芝麻油",
        "香油",
        # 水類
        "水",
        "飲用水",
        "開水",
        "高湯",
        "水煮",
        "冷水",
        "熱水",
        "冰水",
        "礦泉水",
        "純水",
        "蒸餾水",
        "米水",
        "蔬菜水",
        "泡菜水",
        "浸泡水",
        "高湯或水",
        "調味料",
    ]
)


def load_recipes(csv_path):
    """載入清理後的 CSV 食譜資料"""
    recipes = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 將 CSV 行轉換為與原 JSON 格式相容的字典
            recipe = {
                "id": row["id"],
                "name": row["name"],
                "url": row["url"],
                "preview_ingredients": row["preview_ingredients"],
                "ingredients": (
                    row["ingredients"].split(" | ") if row["ingredients"] else []
                ),
                "steps": row["steps"].split(" | ") if row["steps"] else [],
                "combined_text": row["combined_text"],
                "image_path": row["image_path"],
            }
            recipes.append(recipe)
    return recipes


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
        documents.append(
            {"id": recipe_id, "name": recipe["name"], "document": document}
        )
    return documents


def save_documents_to_csv(documents, output_path):
    """將食譜文件輸出成 CSV 檔"""
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "document"])
        writer.writeheader()
        writer.writerows(documents)


def main():
    # 取得腳本所在目錄和專案根目錄
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))
    cleaned_csv_dir = os.path.join(project_root, "cleaned_csv")

    # 如果有命令列參數，使用指定的菜名；否則自動尋找
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            # 處理所有菜名資料夾
            vegetable_dirs = [
                d
                for d in os.listdir(cleaned_csv_dir)
                if os.path.isdir(os.path.join(cleaned_csv_dir, d))
            ]
            if not vegetable_dirs:
                print("❌ 在 cleaned_csv 目錄中找不到任何菜名資料夾")
                sys.exit(1)
        else:
            vegetable_name = sys.argv[1]
            vegetable_dir = os.path.join(cleaned_csv_dir, vegetable_name)
            if not os.path.exists(vegetable_dir):
                print(f"❌ 找不到菜名資料夾：{vegetable_dir}")
                sys.exit(1)
            vegetable_dirs = [vegetable_name]
    else:
        # 自動尋找 cleaned_csv 目錄中的菜名資料夾
        vegetable_dirs = [
            d
            for d in os.listdir(cleaned_csv_dir)
            if os.path.isdir(os.path.join(cleaned_csv_dir, d))
        ]

        if not vegetable_dirs:
            print("❌ 在 cleaned_csv 目錄中找不到任何菜名資料夾")
            sys.exit(1)
        elif len(vegetable_dirs) > 1:
            print("🔍 找到多個菜名資料夾：")
            for i, folder in enumerate(vegetable_dirs, 1):
                print(f"  {i}. {folder}")
            print("請指定要處理的菜名：python generate_documents.py <菜名>")
            print("或使用 --all 處理所有菜名：python generate_documents.py --all")
            sys.exit(1)

    # 處理每個菜名資料夾
    for vegetable_name in vegetable_dirs:
        vegetable_dir = os.path.join(cleaned_csv_dir, vegetable_name)

        # 設定輸入和輸出路徑
        input_csv_path = os.path.join(vegetable_dir, f"{vegetable_name}_清理後食譜.csv")
        output_csv_path = os.path.join(
            vegetable_dir, f"{vegetable_name}_recipe_documents.csv"
        )

        if not os.path.exists(input_csv_path):
            print(f"❌ 找不到 CSV 檔案：{input_csv_path}")
            continue

        print(f"📁 處理菜名：{vegetable_name}")
        print(f"📄 讀取檔案：{os.path.basename(input_csv_path)}")

        # 處理資料
        recipes = load_recipes(input_csv_path)
        documents = generate_documents(recipes)
        save_documents_to_csv(documents, output_csv_path)

        print(f"✅ 已產生 {len(documents)} 筆食譜文件")
        print(f"💾 儲存於：{output_csv_path}")

    print(f"\n🎉 所有菜名處理完成！")


if __name__ == "__main__":
    main()
