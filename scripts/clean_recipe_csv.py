import csv
import json
import os
import re

# 處理單一食材為結構化格式：name, quantity, unit
import re

import re
from fractions import Fraction

# 組合食材拆解邏輯
solid_ingredients = ["米", "糖", "鹽巴", "鹽"]
liquid_ingredients = ["水", "醬油", "油", "高湯", "米酒", "香油"]  # 可依需要擴充

def parse_ingredient(ingredient_str):
    ingredient_str = ingredient_str.strip()
    zh_num_map = {'一':1, '二':2, '兩':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9, '半':0.5}

    # 處理組合食材略...

    # 檢查是否有分數格式
    fraction_match = re.search(r'(\d+/\d+)', ingredient_str)
    if fraction_match:
        quantity_str = fraction_match.group(1)  # 直接保留字串
        quantity_start = fraction_match.start()
        name = ingredient_str[:quantity_start].strip()
        unit = ingredient_str[quantity_start + len(quantity_str):].strip()

        # 如果是固體，保持分數字串不變
        if any(solid in name for solid in solid_ingredients):
            quantity = quantity_str
        else:
            # 液體類可轉成 float 並四捨五入
            quantity_float = round(float(Fraction(quantity_str)), 2)
            quantity = quantity_float

        return {
            "name": name,
            "quantity": quantity,
            "unit": unit or None
        }

    # 處理中文數字或阿拉伯數字
    num_match = re.search(r'([\d\.]+|[一二兩三四五六七八九半]+)', ingredient_str)
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

        unit = remainder[len(quantity_str):].strip()
        return {
            "name": name,
            "quantity": quantity,
            "unit": unit or None
        }

    # 沒有數量，嘗試從尾巴判單位
    # (這部分維持你現有邏輯)
    # ...

    # 沒有匹配，回傳原字串
    return {
        "name": ingredient_str,
        "quantity": None,
        "unit": None
    }



# 清理 ingredients，先以 、 或 , 分隔後去除空白，並回傳清單
def clean_ingredients(ingredients_str):
    items = [i.strip().replace("*", "") for i in ingredients_str.replace("、", ",").split(",") if i.strip()]
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
        reader = csv.DictReader(f, delimiter=';')  # 根據你資料的分隔符是 ;
        for row in reader:
            name = row["食譜名稱"].strip()
            if name in seen_names:
                continue  # 移除重複名稱
            seen_names.add(name)

            ingredients = clean_ingredients(row["詳細食材"])
            structured_ingredients = [parse_ingredient(i) for i in ingredients]  # 結構化處理
            steps = clean_steps(row["做法"])

            # 合併文字欄位（給 NLP 使用）
            combined_text = f"{name}。食材：{'，'.join(ingredients)}。做法：{'，'.join(steps)}。"

            # 修正圖片路徑中的反斜線
            image_path = row["圖片相對路徑"].replace("\\", "/")

            recipes.append({
                "id": row["id"],
                "name": name,
                "url": row["網址"],
                "preview_ingredients": row["預覽食材"],
                "ingredients": ingredients,  # 原始食材清單
                "structured_ingredients": structured_ingredients,  # 新增：結構化版本
                "steps": steps,
                "combined_text": combined_text,
                "image_path": image_path
            })
    return recipes

# 儲存資料為 CSV 與 JSON
def save_clean_data(recipes, output_csv=None, output_json=None):
    if output_csv:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
            fieldnames = ["id", "name", "url", "preview_ingredients", "ingredients", "steps", "combined_text", "image_path"]
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
                    "image_path": r["image_path"]
                })
        print(f"✅ 清理後資料已存成 CSV：{output_csv}")

    if output_json:
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        print(f"✅ 清理後資料已存成 JSON：{output_json}")

# 主程式入口
if __name__ == "__main__":
    input_file = r"D:\AIPE\aipe_project\raw_csv\小白菜_食譜資料.csv"
    output_csv = r"D:\AIPE\aipe_project\cleaned_csv\小白菜_清理後食譜.csv"
    output_json = r"D:\AIPE\aipe_project\cleaned_csv\小白菜_清理後食譜.json"

    cleaned_recipes = load_and_clean_csv(input_file)
    print(f"🔍 讀取並清理完成，共 {len(cleaned_recipes)} 筆食譜")

    save_clean_data(cleaned_recipes, output_csv=output_csv, output_json=output_json)
