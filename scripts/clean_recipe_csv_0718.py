import csv
import json
import os
import re
from fractions import Fraction

# 常見調味料清單（可擴充）
COMMON_SEASONINGS = [
    "白胡椒粉",
    "黑胡椒粉",
    "白胡椒鹽",
    "胡椒粉",
    "胡椒鹽",
    "鹽巴",
    "鹽",
    "砂糖",
    "糖",
    "冰糖",
    "醬油",
    "味醂",
    "米酒",
    "香油",
    "麻油",
    "蠔油",
    "辣椒醬",
    "豆瓣醬",
    "辣椒粉",
    "五香粉",
    "八角粉",
    "回香粉",
    "花椒粉",
    "孜然粉",
    "咖哩粉",
    "番茄醬",
    "烏醋",
    "醋",
    "味噌",
    "雞粉",
    "雞精",
    "高湯粉",
    "味精",
]


# 拆分複合調味料函式
def split_seasoning_compounds(ingredient: str) -> list[str]:
    """
    將複合調味料詞拆成多筆（例如：鹽巴白胡椒粉 → ['鹽巴', '白胡椒粉']）
    以 COMMON_SEASONINGS 中較長的詞優先匹配拆分。
    """
    seasonings_sorted = sorted(COMMON_SEASONINGS, key=len, reverse=True)
    results = []
    rest = ingredient
    while rest:
        matched = False
        for s in seasonings_sorted:
            if rest.startswith(s):
                results.append(s)
                rest = rest[len(s) :].strip()
                matched = True
                break
        if not matched:
            # 找不到匹配就直接把剩下字串加入
            results.append(rest)
            break
    return results


# 組合食材拆解邏輯
solid_ingredients = ["米", "糖", "鹽巴", "鹽"]
liquid_ingredients = ["水", "醬油", "油", "高湯", "米酒", "香油"]  # 可依需要擴充


def parse_ingredient(ingredient_str):
    ingredient_str = ingredient_str.strip()
    zh_num_map = {
        "一": 1,
        "二": 2,
        "兩": 2,
        "三": 3,
        "四": 4,
        "五": 5,
        "六": 6,
        "七": 7,
        "八": 8,
        "九": 9,
        "半": 0.5,
    }

    # 修正 05 → 0.5 類型錯誤
    ingredient_str = re.sub(r"(?<=\D)0(\d)", r"0.\1", ingredient_str)

    # 處理少許、隨意等無數字量詞直接返回
    if ingredient_str in ["少許", "隨意", "適量", "依喜好"]:
        return {"name": None, "quantity": None, "unit": ingredient_str}

    # 檢查是否有分數格式
    fraction_match = re.search(r"(\d+/\d+)", ingredient_str)
    if fraction_match:
        quantity_str = fraction_match.group(1)  # 直接保留字串
        quantity_start = fraction_match.start()
        name = ingredient_str[:quantity_start].strip()
        unit = ingredient_str[quantity_start + len(quantity_str) :].strip()

        # 如果是固體，保持分數字串不變
        if any(solid in name for solid in solid_ingredients):
            quantity = quantity_str
        else:
            # 液體類可轉成 float 並四捨五入
            quantity_float = round(float(Fraction(quantity_str)), 2)
            quantity = quantity_float

        # 避免空 name
        if not name:
            return {"name": None, "quantity": quantity, "unit": unit or None}
        return {"name": name, "quantity": quantity, "unit": unit or None}

    # 處理中文數字或阿拉伯數字
    num_match = re.search(r"([\d\.]+|[一二兩三四五六七八九半]+)", ingredient_str)
    if num_match:
        quantity_str = num_match.group(1)
        quantity_start = num_match.start()
        name = ingredient_str[:quantity_start].strip()
        remainder = ingredient_str[quantity_start:].strip()

        if quantity_str in zh_num_map:
            quantity_float = zh_num_map[quantity_str]
        else:
            try:
                quantity_float = float(quantity_str)
            except:
                quantity_float = None

        if quantity_float is not None:
            if any(solid in name for solid in solid_ingredients):
                quantity = quantity_float  # 固體四捨五入不強制，原數字即可
            else:
                quantity = round(quantity_float, 2)  # 液體四捨五入2位
        else:
            quantity = None

        unit = remainder[len(quantity_str) :].strip()

        # 避免空 name 產生獨立數量或量詞項目
        if not name:
            return {"name": None, "quantity": quantity, "unit": unit or None}

        # 若 unit 是像「少許」「隨意」這類詞，把 quantity 設為 None，unit 保留
        if unit in ["少許", "隨意", "適量", "依喜好"]:
            return {"name": name, "quantity": None, "unit": unit}

        return {"name": name, "quantity": quantity, "unit": unit or None}

    # 沒有數量，嘗試從尾巴判單位（可依需要補充）

    # 沒有匹配，回傳原字串
    return {"name": ingredient_str, "quantity": None, "unit": None}


# 清理 ingredients，先以 、 或 , 分隔後去除空白，並回傳清單
def clean_ingredients(ingredients_str):
    items = [
        i.strip().replace("*", "")
        for i in ingredients_str.replace("、", ",").split(",")
        if i.strip()
    ]
    return items


# 將步驟字串以 | 或 / 等符號切開並清理空白
def clean_steps(steps_str):
    # 嘗試使用多種分隔符號
    for sep in ["|", "/", "，", ","]:
        if sep in steps_str:
            return [s.strip() for s in steps_str.split(sep) if s.strip()]
    # 若無分隔符號，視為單一步驟
    return [steps_str.strip()]


# 主清洗函數：讀取 CSV 並轉成結構化 JSON 清單
def load_and_clean_csv(file_path):
    recipes = []
    seen_names = set()

    with open(file_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")  # 根據你資料的分隔符是 ;
        for row in reader:
            name = row["食譜名稱"].strip()
            if name in seen_names:
                continue  # 移除重複名稱
            seen_names.add(name)

            # 先清理食材字串
            raw_ingredients = clean_ingredients(row["詳細食材"])

            # 用拆分調味料函式拆解複合調味料，再平坦展開
            expanded_ingredients = []
            for ing in raw_ingredients:
                split_ings = split_seasoning_compounds(ing)
                expanded_ingredients.extend(split_ings)

            # 結構化解析
            structured_ingredients = [parse_ingredient(i) for i in expanded_ingredients]
            # 過濾掉 name 為 None 的無效項目
            structured_ingredients = [i for i in structured_ingredients if i["name"]]

            steps = clean_steps(row["做法"])

            combined_text = f"{name}。食材：{'，'.join(expanded_ingredients)}。做法：{'，'.join(steps)}。"

            image_path = row["圖片相對路徑"].replace("\\", "/")

            recipes.append(
                {
                    "id": row["id"],
                    "name": name,
                    "url": row["網址"],
                    "preview_ingredients": row["預覽食材"],
                    "ingredients": expanded_ingredients,
                    "structured_ingredients": structured_ingredients,
                    "steps": steps,
                    "combined_text": combined_text,
                    "image_path": image_path,
                }
            )
    return recipes


# 儲存資料為 CSV 與 JSON
def save_clean_data(recipes, output_csv=None, output_json=None):
    if output_csv:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
            fieldnames = [
                "id",
                "name",
                "url",
                "preview_ingredients",
                "ingredients",
                "steps",
                "combined_text",
                "image_path",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in recipes:
                writer.writerow(
                    {
                        "id": r["id"],
                        "name": r["name"],
                        "url": r["url"],
                        "preview_ingredients": r["preview_ingredients"],
                        "ingredients": " | ".join(r["ingredients"]),
                        "steps": " | ".join(r["steps"]),
                        "combined_text": r["combined_text"],
                        "image_path": r["image_path"],
                    }
                )
        print(f"✅ 清理後資料已存成 CSV：{output_csv}")

    if output_json:
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        print(f"✅ 清理後資料已存成 JSON：{output_json}")


# 主程式入口，使用相對路徑定位檔案
if __name__ == "__main__":
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))

    input_file = os.path.join(project_root, "raw_csv", "小白菜_食譜資料.csv")
    output_csv = os.path.join(project_root, "cleaned_csv", "小白菜_清理後食譜.csv")
    output_json = os.path.join(project_root, "cleaned_csv", "小白菜_清理後食譜.json")

    cleaned_recipes = load_and_clean_csv(input_file)
    print(f"🔍 讀取並清理完成，共 {len(cleaned_recipes)} 筆食譜")

    save_clean_data(cleaned_recipes, output_csv=output_csv, output_json=output_json)
