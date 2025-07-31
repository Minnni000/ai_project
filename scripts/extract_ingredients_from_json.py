#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 cleaned_csv 目錄中的 JSON 檔案提取食材資料
輸出格式：id,預覽食材,詳細食材
"""

import json
import csv
from pathlib import Path


def extract_ingredients_from_json():
    """從所有 JSON 檔案提取食材資料"""
    
    # 設定路徑
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    cleaned_csv_dir = project_root / "cleaned_csv"
    database_dir = project_root / "database"
    
    # 確保 database 目錄存在
    database_dir.mkdir(exist_ok=True)
    
    output_file = database_dir / "extracted_ingredients.csv"
    
    print("🔍 開始提取食材資料...")
    
    # 尋找所有 JSON 檔案
    json_files = list(cleaned_csv_dir.glob("*/*_清理後食譜.json"))
    
    if not json_files:
        print("❌ 找不到任何 JSON 檔案")
        return
    
    print(f"📋 找到 {len(json_files)} 個檔案")
    
    all_ingredients = []
    
    # 處理每個檔案
    for json_file in json_files:
        print(f"📄 處理：{json_file}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                recipes = json.load(f)
            
            for recipe in recipes:
                recipe_id = recipe.get("id")
                preview_ingredients = recipe.get("preview_ingredients", "")
                ingredients = recipe.get("ingredients", [])
                
                if not recipe_id:
                    continue
                
                # 分割預覽食材
                if preview_ingredients:
                    preview_list = [item.strip() for item in preview_ingredients.replace('、', ',').split(',') if item.strip()]
                    
                    for preview_item in preview_list:
                        # 找對應的詳細食材
                        detailed_item = ""
                        for ingredient in ingredients:
                            if preview_item in ingredient:
                                detailed_item = ingredient
                                break
                        
                        all_ingredients.append([recipe_id, preview_item, detailed_item])
                        
        except Exception as e:
            print(f"❌ 處理檔案 {json_file} 時發生錯誤：{e}")
    
    # 輸出結果
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        
        # 寫入標題
        writer.writerow(['id', '預覽食材', '詳細食材'])
        
        # 寫入資料
        writer.writerows(all_ingredients)
    
    print(f"✅ 完成！共提取 {len(all_ingredients)} 筆食材資料")
    print(f"📄 輸出檔案：{output_file}")


if __name__ == "__main__":
    extract_ingredients_from_json()