import csv
import json
import os
import re
from fractions import Fraction

# ✅ 常見調味料清單，可依需求擴充
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

# ✅ 固體與液體分類食材清單（可擴充使用）
solid_ingredients = ["米", "糖", "鹽巴", "鹽", "白胡椒粉"]
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
                rest = rest[len(s) :].strip()
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

    # ✅ 新增：專門處理複雜格式的解析
    def parse_complex_ingredient(text):
        """處理複雜格式的食材，如 '鮭魚1片(270g)' 或 '檸檬1/4顆'"""

        # 先將全形斜線轉換為半形斜線，並處理 Unicode 分數符號
        text = text.replace('／', '/')
        # 處理 Unicode 分數符號
        unicode_fractions = {
            '¼': '1/4', '½': '1/2', '¾': '3/4',
            '⅐': '1/7', '⅑': '1/9', '⅒': '1/10',
            '⅓': '1/3', '⅔': '2/3', '⅕': '1/5',
            '⅖': '2/5', '⅗': '3/5', '⅘': '4/5',
            '⅙': '1/6', '⅚': '5/6', '⅛': '1/8',
            '⅜': '3/8', '⅝': '5/8', '⅞': '7/8'
        }
        for unicode_frac, normal_frac in unicode_fractions.items():
            text = text.replace(unicode_frac, normal_frac)

        # 模式1: 名稱+範圍數字+單位，如 "水1～2大匙" (優先處理)
        pattern0 = re.match(r'^(.+?)(\d+[～~]\d+)\s*(.+)$', text)
        if pattern0:
            name = pattern0.group(1).strip()
            quantity_range = pattern0.group(2)
            unit = pattern0.group(3).strip()

            return {"name": name, "quantity": quantity_range, "unit": unit}

        # 模式2: 名稱+數量+單位+括號，如 "鮭魚1片(270g)"
        pattern1 = re.match(r'^(.+?)(\d+(?:/\d+)?(?:\.\d+)?)\s*([^\d\s\(]+)(\([^)]*\))?$', text)
        if pattern1:
            name_part = pattern1.group(1).strip()
            quantity_str = pattern1.group(2)
            unit_str = pattern1.group(3).strip()
            bracket_content = pattern1.group(4) or ""

            # 將括號內容加到名稱後面
            name = name_part + bracket_content if bracket_content else name_part

            # 處理分數
            if "/" in quantity_str:
                try:
                    quantity = round(float(Fraction(quantity_str)), 3)
                except ValueError:
                    quantity = quantity_str
            else:
                try:
                    quantity = round(float(quantity_str), 2)
                except ValueError:
                    quantity = quantity_str

            return {"name": name, "quantity": quantity, "unit": unit_str}

        # 模式3: 名稱+分數+單位，如 "檸檬1/4顆" 或 "鹽1/8茶匙"
        pattern2 = re.match(r'^(.+?)(\d+/\d+)\s*([^\d\s]+)$', text)
        if pattern2:
            name = pattern2.group(1).strip()
            quantity_str = pattern2.group(2)
            unit = pattern2.group(3).strip()

            try:
                quantity = round(float(Fraction(quantity_str)), 3)
            except ValueError:
                quantity = quantity_str

            return {"name": name, "quantity": quantity, "unit": unit}

        # 模式4: 名稱+空格+模糊量詞，如 "薑絲 小撮"
        pattern4 = re.match(r'^(.+?)\s+(少許|適量|隨意|依喜好|小撮|一撮|一點|些許|少量)$', text)
        if pattern4:
            name = pattern4.group(1).strip()
            quantity_word = pattern4.group(2).strip()

            return {"name": name, "quantity": quantity_word, "unit": None}

        # 模式5: 名稱+中文數字+單位，如 "九層塔一把"、"薑絲一小撮"、"蘑菇半盒"
        # 但要避免誤判，如 "小磨坊蒜香九層塔適量" 中的 "九" 不是數量
        pattern5 = re.match(r'^(.+?)(一|二|三|四|五|六|七|八|九|十|半)(.+)$', text)
        if pattern5:
            name = pattern5.group(1).strip()
            chinese_num = pattern5.group(2)
            unit = pattern5.group(3).strip()

            # 檢查是否為真正的數量詞，避免誤判食材名稱中的中文數字
            # 如果單位是常見的量詞，才認為是數量
            common_units = ["把", "根", "片", "顆", "個", "條", "支", "束", "小撮", "大撮", "撮", "塊", "杯", "匙", "茶匙", "碗", "斤", "兩", "滴", "份", "瓶", "包", "罐", "籃", "粒", "盒"]

            if unit in common_units:
                # 中文數字轉換
                chinese_to_num = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
                                "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "半": 0.5}
                quantity = chinese_to_num.get(chinese_num, chinese_num)

                return {"name": name, "quantity": quantity, "unit": unit}

        # 模式6: 名稱+模糊量詞結尾，如 "小磨坊蒜香九層塔適量"、"鹽少量"
        pattern6 = re.match(r'^(.+?)(少許|適量|隨意|依喜好|些許|少量)$', text)
        if pattern6:
            name = pattern6.group(1).strip()
            quantity_word = pattern6.group(2)

            return {"name": name, "quantity": quantity_word, "unit": None}



        # 模式7: 複雜名稱+數量+單位，如 "小磨坊-蒜香九層塔1/8茶匙"
        pattern3 = re.match(r'^(.+?)(\d+(?:/\d+)?(?:\.\d+)?)\s*(.+)$', text)
        if pattern3:
            name = pattern3.group(1).strip()
            quantity_str = pattern3.group(2)
            unit = pattern3.group(3).strip()

            # 處理分數
            if "/" in quantity_str:
                try:
                    quantity = round(float(Fraction(quantity_str)), 3)
                except ValueError:
                    quantity = quantity_str
            else:
                try:
                    quantity = round(float(quantity_str), 2)
                except ValueError:
                    quantity = quantity_str

            return {"name": name, "quantity": quantity, "unit": unit}

        # 模式8: 名稱+純數字（無單位），如 "糖0.5"
        pattern7 = re.match(r'^(.+?)(\d+(?:\.\d+)?)$', text)
        if pattern7:
            name = pattern7.group(1).strip()
            quantity_str = pattern7.group(2)

            try:
                quantity = round(float(quantity_str), 2)
            except ValueError:
                quantity = quantity_str

            return {"name": name, "quantity": quantity, "unit": None}

        return None

    # 先嘗試新的複雜格式解析
    complex_result = parse_complex_ingredient(ingredient_str)
    if complex_result:
        return complex_result

    # ✅ 若食材開頭為常見調味料或固體名稱，優先拆解
    possible_names = sorted(
        set(COMMON_SEASONINGS + solid_ingredients + liquid_ingredients),
        key=len,
        reverse=True,
    )
    for known_name in possible_names:
        if ingredient_str.startswith(known_name):
            rest_str = ingredient_str[len(known_name) :].strip()
            name = known_name
            # 嘗試解析後面是否有數量與單位
            # match_rest = re.match(r"([\d\.]+|\d+/\d+|[一二兩三四五六七八九半]+)\s*([^\d\s\.]+)?", rest_str)
            match_rest = re.match(
                r"^([一二兩三四五六七八九半\d./]+)([^\d\s]*)\s*(.*)$", rest_str
            )

            quantity = None
            unit = None
            if match_rest:
                quantity_str = match_rest.group(1)
                unit_str = match_rest.group(2) or ""

                if "/" in quantity_str:
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
            else:
                # 如果沒有匹配到數量，檢查是否為模糊量詞或複合調味料
                for qty_word in ["少許", "適量", "隨意", "依喜好"]:
                    if rest_str == qty_word:
                        quantity = qty_word
                        break
                    elif rest_str.endswith(qty_word):
                        # 可能是複合調味料，如 "白胡椒粉少許"
                        # 檢查去掉量詞後是否還有其他調味料
                        remaining = rest_str[: -len(qty_word)].strip()
                        if remaining and any(
                            remaining.startswith(s) for s in COMMON_SEASONINGS
                        ):
                            # 這是複合調味料，設定量詞
                            quantity = qty_word
                        break

            return {"name": name, "quantity": quantity, "unit": unit}

    # ✅ 處理「少許」「適量」等模糊量詞
    for qty_word in ["少許", "適量", "隨意", "依喜好"]:
        if ingredient_str == qty_word:
            return {"name": None, "quantity": qty_word, "unit": None}
        elif ingredient_str.endswith(qty_word):
            name_part = ingredient_str[: -len(qty_word)].strip()
            return {"name": name_part or None, "quantity": qty_word, "unit": None}

    # ✅ 修正數字格式錯誤：如 05 → 0.5
    ingredient_str = re.sub(r"(?<=\D)0(\d)", r"0.\1", ingredient_str)

    # ✅ 使用正則抓取數量、單位與名稱（改進版）
    # 先處理特殊格式：名稱+數量+單位+括號內容，如 "鮭魚1片(270g)"
    special_match = re.match(r"^(.+?)(\d+(?:/\d+)?(?:\.\d+)?)\s*([^\d\s\(]+)(\([^)]*\))?", ingredient_str)
    if special_match:
        name_part = special_match.group(1).strip()
        quantity_str = special_match.group(2)
        unit_str = special_match.group(3).strip()
        bracket_content = special_match.group(4) or ""

        # 將括號內容加到名稱後面
        name = name_part + bracket_content if bracket_content else name_part

        # 處理分數
        if "/" in quantity_str:
            try:
                quantity = round(float(Fraction(quantity_str)), 3)
            except ValueError:
                quantity = quantity_str
        else:
            try:
                quantity = round(float(quantity_str), 2)
            except ValueError:
                quantity = quantity_str

        return {"name": name, "quantity": quantity, "unit": unit_str}

    # 原有的正則匹配邏輯
    match = re.search(
        r"([\d\.]+|\d+/\d+|[一二兩三四五六七八九半]+)\s*([^a-zA-Z\d\s]*)(.*)",
        ingredient_str,
    )

    if match:
        quantity_str = match.group(1)
        unit_str = match.group(2).strip()
        name_candidate = match.group(3).strip()

        quantity = None
        # ✅ 處理數字轉換（含分數與中文）
        if "/" in quantity_str:
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
                    remaining_str = ingredient_str[len(s) :].strip()
                    num_unit_match = re.match(
                        r"([\d\.]+|\d+/\d+|[一二兩三四五六七八九半]+)\s*(.*)",
                        remaining_str,
                    )
                    if num_unit_match:
                        qty_s = num_unit_match.group(1)
                        unit_s = num_unit_match.group(2).strip()
                        if "/" in qty_s:
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
                pre_quantity_part = ingredient_str[: match.start()].strip()
                if pre_quantity_part:
                    name = pre_quantity_part

                post_quantity_part = ingredient_str[match.end(1) :].strip()
                unit_and_name_match = re.match(
                    r"^([^\d\s]+)?\s*(.*)", post_quantity_part
                )

                if unit_and_name_match:
                    possible_unit = unit_and_name_match.group(1)
                    possible_name = unit_and_name_match.group(2)

                    common_units = [
                        "杯",
                        "小匙",
                        "大匙",
                        "克",
                        "毫升",
                        "個",
                        "顆",
                        "片",
                        "段",
                        "碗",
                        "包",
                        "把",
                        "小把",
                        "米杯",
                        "根",
                        "邊",
                        "g",
                        "ml",
                        "kg",
                        "l",
                    ]
                    if possible_unit and any(u in possible_unit for u in common_units):
                        unit = possible_unit
                        name_from_unit_part = possible_name.strip()
                        name = (
                            name + name_from_unit_part if name else name_from_unit_part
                        )
                    else:
                        name = (
                            name + " " + post_quantity_part
                            if name
                            else post_quantity_part
                        )
                        unit = None

            if not name and unit:
                name = unit
                unit = None

            # ✅ 嘗試從名稱尾部抽出常見單位（使用上面已定義的 common_units）
            if name and not unit:
                for u in sorted(common_units, key=len, reverse=True):
                    if name.endswith(u):
                        name = name[: -len(u)].strip()
                        unit = u
                        break

            if not name:
                pre_num_part = ingredient_str[: match.start()].strip()
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

            structured_ingredients = [
                parse_ingredient(ing_str) for ing_str in expanded_ingredients
            ]

            # ✅ 處理複合調味料拆分，例如「鹽巴白胡椒粉少許」→ 拆分成多個食材
            # 只處理真正的複合調味料（沒有明確數量單位，且包含多個調味料名稱）
            expanded_structured_ingredients = []
            for i, ingredient in enumerate(structured_ingredients):
                original_str = (
                    expanded_ingredients[i] if i < len(expanded_ingredients) else ""
                )

                # 只有在以下條件都滿足時才進行拆分：
                # 1. 有食材名稱
                # 2. 只有模糊量詞如"少許"，沒有明確數量和單位
                # 3. 原始字串確實包含多個調味料且沒有數字
                should_split = (
                    ingredient["name"]
                    and ingredient["quantity"] in ["少許", "適量", "隨意", "依喜好"]
                    and ingredient["unit"] is None
                    and not re.search(
                        r"[\d/一二兩三四五六七八九半]",
                        original_str.replace("少許", "").replace("適量", ""),
                    )
                )

                if should_split:
                    # 移除量詞後檢查是否為複合調味料
                    check_str = original_str
                    qty_word = ingredient["quantity"]
                    for qw in ["少許", "適量", "隨意", "依喜好"]:
                        if check_str.endswith(qw):
                            check_str = check_str[: -len(qw)].strip()
                            break

                    compound_parts = split_seasoning_compounds(check_str)
                    if len(compound_parts) > 1:
                        # 確認拆分出的都是調味料
                        all_seasonings = all(
                            part in COMMON_SEASONINGS for part in compound_parts
                        )
                        if all_seasonings:
                            # 拆分成多個食材
                            for part in compound_parts:
                                expanded_structured_ingredients.append(
                                    {"name": part, "quantity": qty_word, "unit": None}
                                )
                        else:
                            # 不是全部都是調味料，保持原樣
                            expanded_structured_ingredients.append(ingredient)
                    else:
                        expanded_structured_ingredients.append(ingredient)
                else:
                    expanded_structured_ingredients.append(ingredient)

            structured_ingredients = expanded_structured_ingredients

            # ✅ 後處理：補足沒有名稱但有數量單位的欄位
            final_structured_ingredients = []
            i = 0
            while i < len(structured_ingredients):
                current_ing = structured_ingredients[i]
                if current_ing["name"] is None and (
                    current_ing["quantity"] is not None
                    or current_ing["unit"] is not None
                ):
                    if (
                        final_structured_ingredients
                        and final_structured_ingredients[-1]["quantity"] is None
                        and final_structured_ingredients[-1]["unit"] is None
                    ):
                        prev_ing = final_structured_ingredients[-1]
                        combined_str_parts = [prev_ing["name"]]
                        if current_ing["quantity"] is not None:
                            combined_str_parts.append(str(current_ing["quantity"]))
                        if current_ing["unit"] is not None:
                            combined_str_parts.append(current_ing["unit"])
                        combined_str = "".join(combined_str_parts).strip()
                        reparsed_combined = parse_ingredient(combined_str)
                        if reparsed_combined["name"] == prev_ing["name"] and (
                            reparsed_combined["quantity"] is not None
                            or reparsed_combined["unit"] is not None
                        ):
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
                if (
                    item["name"] in ["糖", "胡椒粉", "米酒"]
                    and item["quantity"] is None
                ):
                    item["quantity"] = "少許"
                    item["unit"] = None

            # ✅ 移除完全為空的項目（應該放最後）
            final_structured_ingredients = [
                item
                for item in final_structured_ingredients
                if item["name"] is not None
                or item["quantity"] is not None
                or item["unit"] is not None
            ]
            # ✅ 組合成最終的食材清單
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
                    "structured_ingredients": final_structured_ingredients,
                    "steps": steps,
                    "combined_text": combined_text,
                    "image_path": image_path,
                }
            )

    return recipes


# ✅ 儲存資料為 CSV / JSON
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


# ✅ 程式主入口：讀取原始檔案並執行清理與儲存
if __name__ == "__main__":
    import os
    import sys
    import glob

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, ".."))
    raw_csv_dir = os.path.join(project_root, "raw_csv")

    # 如果有命令列參數，使用指定的檔案；否則處理所有 CSV 檔案
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            # 處理所有檔案
            csv_files = glob.glob(os.path.join(raw_csv_dir, "*_食譜資料.csv"))
        else:
            # 處理指定檔案
            input_filename = sys.argv[1]
            csv_files = [os.path.join(raw_csv_dir, input_filename)]
    else:
        # 自動尋找並詢問
        csv_files = glob.glob(os.path.join(raw_csv_dir, "*_食譜資料.csv"))
        if not csv_files:
            print("❌ 在 raw_csv 目錄中找不到符合格式的 CSV 檔案（*_食譜資料.csv）")
            sys.exit(1)
        elif len(csv_files) > 1:
            print("🔍 找到多個 CSV 檔案：")
            for i, file in enumerate(csv_files, 1):
                print(f"  {i}. {os.path.basename(file)}")
            print("請指定要處理的檔案：python clean_recipe_csv_0720.py <檔名>")
            print("或使用 --all 處理所有檔案：python clean_recipe_csv_0720.py --all")
            sys.exit(1)

    # 處理每個檔案
    for input_file in csv_files:
        if not os.path.exists(input_file):
            print(f"❌ 檔案不存在：{input_file}")
            continue

        # 從檔名中提取菜名
        input_filename = os.path.basename(input_file)
        vegetable_name = input_filename.split("_")[0]

        print(f"\n📁 處理檔案：{input_filename}")
        print(f"🥬 菜名：{vegetable_name}")

        # 建立輸出目錄和檔案路徑
        output_base_dir = os.path.join(project_root, "cleaned_csv")
        output_vegetable_dir = os.path.join(output_base_dir, vegetable_name)

        output_csv = os.path.join(
            output_vegetable_dir, f"{vegetable_name}_清理後食譜.csv"
        )
        output_json = os.path.join(
            output_vegetable_dir, f"{vegetable_name}_清理後食譜.json"
        )

        cleaned_recipes = load_and_clean_csv(input_file)
        print(f"🔍 讀取並清理完成，共 {len(cleaned_recipes)} 筆食譜")

        save_clean_data(cleaned_recipes, output_csv=output_csv, output_json=output_json)

    print(f"\n✅ 所有檔案處理完成！")
