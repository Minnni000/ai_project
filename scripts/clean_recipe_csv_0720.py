import csv
import json
import os
import re
from fractions import Fraction

# ✅ 常見調味料清單，可依需求擴充
COMMON_SEASONINGS = [
    "白胡椒粉", "黑胡椒粉", "白胡椒鹽", "胡椒粉", "胡椒鹽", "鹽巴", "鹽", "砂糖", "糖", "冰糖",
    "醬油", "味醂", "米酒", "香油", "麻油", "蠔油", "辣椒醬", "豆瓣醬", "辣椒粉", "五香粉",
    "八角粉", "回香粉", "花椒粉", "孜然粉", "咖哩粉", "番茄醬", "烏醋", "醋", "味噌", "雞粉",
    "雞精", "高湯粉", "味精"
]

# ✅ 固體與液體分類食材清單（可擴充使用）
solid_ingredients = ["米", "糖", "鹽巴", "鹽"]
liquid_ingredients = ["水", "醬油", "油", "高湯", "米酒", "香油"]


# ✅ 拆分連在一起的複合調味料詞，例如「鹽巴白胡椒粉」→ ['鹽巴', '白胡椒粉']
def split_seasoning_compounds(ingredient: str) -> list[str]:
    seasonings_sorted = sorted(COMMON_SEASONINGS, key=len, reverse=True)
    results = []
    rest = ingredient
    while rest:
        matched = False
        for s in seasonings_sorted:
            if rest.startswith(s):
                results.append(s)
                rest = rest[len(s):].strip()
                matched = True
                break
        if not matched:
            results.append(rest)
            break
    return results


# ✅ 將原始食材字串轉為結構化格式：{name, quantity, unit}
def parse_ingredient(ingredient_str):
    ingredient_str = ingredient_str.strip()

    # 中文數字對照表（半 → 0.5）
    zh_num_map = {
        "一": 1, "二": 2, "兩": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "半": 0.5,
    }

    # ✅ 若食材開頭為常見調味料或固體名稱，優先拆解
    possible_names = sorted(set(COMMON_SEASONINGS + solid_ingredients + liquid_ingredients), key=len, reverse=True)
    for known_name in possible_names:
        if ingredient_str.startswith(known_name):
            rest_str = ingredient_str[len(known_name):].strip()
            name = known_name
            # 嘗試解析後面是否有數量與單位
            # match_rest = re.match(r"([\d\.]+|\d+/\d+|[一二兩三四五六七八九半]+)\s*([^\d\s\.]+)?", rest_str)
            match_rest = re.match(r"^([一二兩三四五六七八九半\d./]+)([^\d\s]*)\s*(.*)$", rest_str)

            quantity = None
            unit = None
            if match_rest:
                quantity_str = match_rest.group(1)
                unit_str = match_rest.group(2) or ""

                if '/' in quantity_str:
                    try:
                        quantity = round(float(Fraction(quantity_str)), 2)
                    except ValueError:
                        quantity = quantity_str
                elif quantity_str in zh_num_map:
                    quantity = zh_num_map[quantity_str]
                else:
                    try:
                        quantity = round(float(quantity_str), 2)
                    except ValueError:
                        quantity = quantity_str

                unit = unit_str.strip() if unit_str else None

            return {"name": name, "quantity": quantity, "unit": unit}

    # ✅ 處理「少許」「適量」等模糊量詞
    for qty_word in ["少許", "適量", "隨意", "依喜好"]:
        if ingredient_str == qty_word:
            return {"name": None, "quantity": qty_word, "unit": None}
        elif ingredient_str.endswith(qty_word):
            name_part = ingredient_str[:-len(qty_word)].strip()
            return {"name": name_part or None, "quantity": qty_word, "unit": None}

    # ✅ 修正數字格式錯誤：如 05 → 0.5
    ingredient_str = re.sub(r"(?<=\D)0(\d)", r"0.\1", ingredient_str)

    # ✅ 使用正則抓取數量、單位與名稱
    match = re.search(r"([\d\.]+|\d+/\d+|[一二兩三四五六七八九半]+)\s*([^a-zA-Z\d\s]*)(.*)", ingredient_str)

    if match:
        quantity_str = match.group(1)
        unit_str = match.group(2).strip()
        name_candidate = match.group(3).strip()

        quantity = None
        # ✅ 處理數字轉換（含分數與中文）
        if '/' in quantity_str:
            try:
                quantity = round(float(Fraction(quantity_str)), 2)
            except ValueError:
                quantity = quantity_str
        elif quantity_str in zh_num_map:
            quantity = zh_num_map[quantity_str]
        else:
            try:
                quantity = round(float(quantity_str), 2)
            except ValueError:
                quantity = quantity_str

        # ✅ 從原始字串中進一步判斷剩餘部分的單位與名稱
        potential_unit_index = ingredient_str.find(quantity_str) + len(quantity_str)
        remaining_after_quantity = ingredient_str[potential_unit_index:].strip()

        # ✅ 嘗試解析單位與名稱
        unit_match = re.match(r"^([^\d\s\.]+\b)?\s*(.*)", remaining_after_quantity)
        if unit_match:
            unit_candidate = unit_match.group(1) or ""
            name_candidate_from_remainder = unit_match.group(2)

            name = name_candidate_from_remainder.strip()
            unit = unit_candidate.strip()

            # ✅ 如果開頭是調味料，直接指定為名稱
            found_seasoning_as_name = False
            for s in sorted(COMMON_SEASONINGS, key=len, reverse=True):
                if ingredient_str.startswith(s):
                    name = s
                    remaining_str = ingredient_str[len(s):].strip()
                    num_unit_match = re.match(r"([\d\.]+|\d+/\d+|[一二兩三四五六七八九半]+)\s*(.*)", remaining_str)
                    if num_unit_match:
                        qty_s = num_unit_match.group(1)
                        unit_s = num_unit_match.group(2).strip()
                        if '/' in qty_s:
                            try:
                                quantity = round(float(Fraction(qty_s)), 2)
                            except ValueError:
                                quantity = qty_s
                        elif qty_s in zh_num_map:
                            quantity = zh_num_map[qty_s]
                        else:
                            try:
                                quantity = round(float(qty_s), 2)
                            except ValueError:
                                quantity = qty_s
                        unit = unit_s
                    else:
                        # 可能是「鹽少許」這種狀況
                        if remaining_str in ["少許", "適量", "隨意", "依喜好"]:
                            quantity = remaining_str
                            unit = None
                        else:
                            quantity = None
                            unit = remaining_str if remaining_str else None
                    found_seasoning_as_name = True
                    break

            if not found_seasoning_as_name:
                # ✅ 如果名稱在數量前，補上
                pre_quantity_part = ingredient_str[:match.start()].strip()
                if pre_quantity_part:
                    name = pre_quantity_part

                post_quantity_part = ingredient_str[match.end(1):].strip()
                unit_and_name_match = re.match(r"^([^\d\s]+)?\s*(.*)", post_quantity_part)

                if unit_and_name_match:
                    possible_unit = unit_and_name_match.group(1)
                    possible_name = unit_and_name_match.group(2)

                    common_units = ["杯", "小匙", "大匙", "克", "毫升", "個", "顆", "片", "段", "碗", "包", "把", "小把", "米杯", "根"]
                    if possible_unit and any(u in possible_unit for u in common_units):
                        unit = possible_unit
                        name_from_unit_part = possible_name.strip()
                        name = name + name_from_unit_part if name else name_from_unit_part
                    else:
                        name = name + " " + post_quantity_part if name else post_quantity_part
                        unit = None

            if not name and unit:
                name = unit
                unit = None

            # ✅ 嘗試從名稱尾部抽出常見單位
            common_units = ["杯", "小匙", "大匙", "克", "毫升", "個", "顆", "片", "段", "碗", "包", "小把", "米杯"]
            if name and not unit:
                for u in sorted(common_units, key=len, reverse=True):
                    if name.endswith(u):
                        name = name[:-len(u)].strip()
                        unit = u
                        break

            if not name:
                pre_num_part = ingredient_str[:match.start()].strip()
                if pre_num_part:
                    name = pre_num_part

            return {"name": name or None, "quantity": quantity, "unit": unit or None}

    # ❌ 沒有數字就視為純名稱
    return {"name": ingredient_str, "quantity": None, "unit": None}


# ✅ 拆解食材字串為清單
def clean_ingredients(ingredients_str):
    items = [
        i.strip().replace("*", "")
        for i in ingredients_str.replace("、", ",").split(",")
        if i.strip()
    ]
    return items


# ✅ 拆解步驟字串為清單
def clean_steps(steps_str):
    for sep in ["|", "/", "，", ","]:
        if sep in steps_str:
            return [s.strip() for s in steps_str.split(sep) if s.strip()]
    return [steps_str.strip()]


# ✅ 主函數：讀取並清理 CSV 檔案內容
def load_and_clean_csv(file_path):
    recipes = []
    seen_names = set()

    with open(file_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            name = row["食譜名稱"].strip()
            if name in seen_names:
                continue  # 去除重複食譜名稱
            seen_names.add(name)

            raw_ingredients = clean_ingredients(row["詳細食材"])
            expanded_ingredients = raw_ingredients

            structured_ingredients = [parse_ingredient(ing_str) for ing_str in expanded_ingredients]

            # ✅ 後處理：補足沒有名稱但有數量單位的欄位
            final_structured_ingredients = []
            i = 0
            while i < len(structured_ingredients):
                current_ing = structured_ingredients[i]
                if current_ing["name"] is None and (current_ing["quantity"] is not None or current_ing["unit"] is not None):
                    if final_structured_ingredients and final_structured_ingredients[-1]["quantity"] is None and final_structured_ingredients[-1]["unit"] is None:
                        prev_ing = final_structured_ingredients[-1]
                        combined_str_parts = [prev_ing["name"]]
                        if current_ing["quantity"] is not None:
                            combined_str_parts.append(str(current_ing["quantity"]))
                        if current_ing["unit"] is not None:
                            combined_str_parts.append(current_ing["unit"])
                        combined_str = "".join(combined_str_parts).strip()
                        reparsed_combined = parse_ingredient(combined_str)
                        if reparsed_combined["name"] == prev_ing["name"] and (reparsed_combined["quantity"] is not None or reparsed_combined["unit"] is not None):
                            final_structured_ingredients[-1] = reparsed_combined
                        else:
                            final_structured_ingredients.append(current_ing)
                    else:
                        final_structured_ingredients.append(current_ing)
                else:
                    final_structured_ingredients.append(current_ing)
                i += 1

        
            # ✅ 最後補齊一些預設值（特別處理「鹽」為 1/2 小匙，且保留分數）
            for item in final_structured_ingredients:
                # 不要強制修改鹽，讓 parse_ingredient決定
                if item["name"] in ["糖", "胡椒粉", "米酒"] and item["quantity"] is None:
                    item["quantity"] = "少許"
                    item["unit"] = None

                elif item["name"] in ["糖", "胡椒粉", "米酒"] and item["quantity"] is None:
                    item["quantity"] = "少許"
                    item["unit"] = None


            # ✅ 移除完全為空的項目（應該放最後）
            final_structured_ingredients = [
                item for item in final_structured_ingredients
                if item["name"] is not None or item["quantity"] is not None or item["unit"] is not None
            ]
            # ✅ 組合成最終的食材清單
            steps = clean_steps(row["做法"])
            combined_text = f"{name}。食材：{'，'.join(expanded_ingredients)}。做法：{'，'.join(steps)}。"
            image_path = row["圖片相對路徑"].replace("\\", "/")

            recipes.append({
                "id": row["id"],
                "name": name,
                "url": row["網址"],
                "preview_ingredients": row["預覽食材"],
                "ingredients": expanded_ingredients,
                "structured_ingredients": final_structured_ingredients,
                "steps": steps,
                "combined_text": combined_text,
                "image_path": image_path,
            })

    return recipes


# ✅ 儲存資料為 CSV / JSON
def save_clean_data(recipes, output_csv=None, output_json=None):
    if output_csv:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
            fieldnames = [
                "id", "name", "url", "preview_ingredients",
                "ingredients", "steps", "combined_text", "image_path"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in recipes:
                writer.writerow({
                    "id": r["id"],
                    "name": r["name"],
                    "url": r["url"],
                    "preview_ingredients": r["preview_ingredients"],
                    "ingredients": " | ".join(r["ingredients"]),
                    "steps": " | ".join(r["steps"]),
                    "combined_text": r["combined_text"],
                    "image_path": r["image_path"],
                })
        print(f"✅ 清理後資料已存成 CSV：{output_csv}")

    if output_json:
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        print(f"✅ 清理後資料已存成 JSON：{output_json}")


# ✅ 程式主入口：讀取原始檔案並執行清理與儲存
if __name__ == "__main__":
    import os

    base_dir = os.path.dirname(os.path.abspath(__file__))  # 當前執行檔所在資料夾
    project_root = os.path.abspath(os.path.join(base_dir, ".."))  # 上層資料夾作為專案根目錄

    input_file = os.path.join(project_root, "raw_csv", "小白菜_食譜資料.csv")
    output_csv_dir = os.path.join(project_root, "cleaned_csv")
    output_csv = os.path.join(output_csv_dir, "小白菜_清理後食譜.csv")
    output_json = os.path.join(output_csv_dir, "小白菜_清理後食譜.json")

    cleaned_recipes = load_and_clean_csv(input_file)
    print(f"🔍 讀取並清理完成，共 {len(cleaned_recipes)} 筆食譜")

    save_clean_data(cleaned_recipes, output_csv=output_csv, output_json=output_json)
