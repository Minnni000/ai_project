#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 cleaned_csv 中提取食譜資料建立多個資料庫

功能：
1. 主食譜資料庫 (main_recipe_database.csv)：基本食譜資訊
2. 食材資料庫 (ingredient_database.csv)：詳細食材資訊
3. 食譜步驟資料庫 (recipe_steps_database.csv)：食譜步驟資訊
4. 重新命名欄位並統一格式
5. 轉換為相對路徑
6. 輸出到 database 目錄

使用方法：
python create_database.py                    # 互動式選擇
python create_database.py 九層塔             # 建立指定蔬菜的主食譜資料庫
python create_database.py ingredient         # 建立所有蔬菜的食材資料庫
python create_database.py ingredient 九層塔  # 建立指定蔬菜的食材資料庫
python create_database.py steps              # 建立所有蔬菜的食譜步驟資料庫
python create_database.py steps 九層塔       # 建立指定蔬菜的食譜步驟資料庫
"""

import sys
import pandas as pd
from pathlib import Path


class DatabaseCreator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.project_root = self.base_dir.parent
        self.cleaned_csv_dir = self.project_root / "cleaned_csv"
        self.database_dir = self.project_root / "database"

        # 確保 database 目錄存在
        self.database_dir.mkdir(exist_ok=True)

        # 欄位對應關係
        self.field_mapping = {
            "id": "id",
            "name": "recipe",
            "url": "食譜網址來源",
            "image_path": "image_path"
        }
    
    def convert_to_relative_path(self, image_path):
        """將圖片路徑轉換為相對路徑"""
        if not image_path:
            return ""
        
        # 移除可能的絕對路徑前綴
        if "\\image\\" in image_path:
            # 提取 image 之後的部分
            relative_part = image_path.split("\\image\\", 1)[1]
            return f"image/{relative_part.replace('\\', '/')}"
        elif "/image/" in image_path:
            relative_part = image_path.split("/image/", 1)[1]
            return f"image/{relative_part}"
        else:
            # 如果已經是相對路徑，確保使用正斜線
            return image_path.replace("\\", "/")



    def process_vegetable_ingredients(self, vege_name):
        """處理單一蔬菜的食材資料，返回處理後的食材資料"""
        print(f"🥬 處理蔬菜食材：{vege_name}")

        # 設定檔案路徑 - 改為讀取 JSON 檔案
        vege_dir = self.cleaned_csv_dir / vege_name
        input_json = vege_dir / f"{vege_name}_清理後食譜.json"

        if not input_json.exists():
            print(f"⚠️  找不到檔案：{input_json}")
            return []

        try:
            # 讀取 JSON 資料
            import json
            with open(input_json, 'r', encoding='utf-8') as f:
                recipes = json.load(f)

            print(f"  📊 讀取到 {len(recipes)} 筆食譜資料")

            # 建立食材資料
            ingredient_data = []
            for recipe in recipes:
                recipe_id = recipe.get("id")
                structured_ingredients = recipe.get("structured_ingredients", [])

                if not recipe_id or not structured_ingredients:
                    continue

                # 處理結構化食材資料
                try:
                    if isinstance(structured_ingredients, list):
                        for ingredient in structured_ingredients:
                            if isinstance(ingredient, dict) and ingredient.get("name"):
                                record = {
                                    "id": recipe_id,
                                    "ingredient": ingredient.get("name", ""),                                    
                                    "quantity": ingredient.get("quantity", ""),
                                    "unit": ingredient.get("unit", "")
                                }
                                ingredient_data.append(record)

                except Exception as e:
                    print(f"  ⚠️  解析食材資料失敗 (ID: {recipe_id}): {e}")
                    continue

            print(f"  ✅ 成功處理 {len(ingredient_data)} 筆食材資料")
            return ingredient_data

        except Exception as e:
            print(f"  ❌ 處理 {vege_name} 食材時發生錯誤：{e}")
            return []
    
    def process_vegetable(self, vege_name):
        """處理單一蔬菜的資料，返回處理後的資料"""
        print(f"🥬 處理蔬菜：{vege_name}")

        # 設定檔案路徑
        vege_dir = self.cleaned_csv_dir / vege_name
        input_csv = vege_dir / f"{vege_name}_清理後食譜.csv"

        if not input_csv.exists():
            print(f"⚠️  找不到檔案：{input_csv}")
            return []

        try:
            # 讀取原始資料
            df = pd.read_csv(input_csv, encoding='utf-8-sig')
            print(f"  📊 讀取到 {len(df)} 筆食譜資料")

            # 檢查必要欄位是否存在
            required_fields = ["id", "name", "url", "image_path"]
            missing_fields = [field for field in required_fields if field not in df.columns]
            if missing_fields:
                print(f"  ❌ 缺少必要欄位：{missing_fields}")
                return []

            # 建立新的資料框
            database_data = []
            for _, row in df.iterrows():
                record = {
                    "id": row["id"],
                    "vege_name": vege_name,  # 統一的蔬菜名稱
                    "recipe": row["name"],
                    "食譜網址來源": row["url"],
                    "image_path": self.convert_to_relative_path(row["image_path"])
                }
                database_data.append(record)

            print(f"  ✅ 成功處理 {len(database_data)} 筆資料")
            return database_data

        except Exception as e:
            print(f"  ❌ 處理 {vege_name} 時發生錯誤：{e}")
            return []
    
    def get_available_vegetables(self):
        """取得所有可用的蔬菜清單"""
        if not self.cleaned_csv_dir.exists():
            return []
        
        vegetables = []
        for item in self.cleaned_csv_dir.iterdir():
            if item.is_dir():
                # 檢查是否有對應的清理後食譜檔案
                csv_file = item / f"{item.name}_清理後食譜.csv"
                if csv_file.exists():
                    vegetables.append(item.name)
        
        return sorted(vegetables)

    def create_ingredient_database(self, target_vegetable=None):
        """建立食材資料庫"""
        print("🥕 食材資料庫建立工具")
        print("=" * 60)

        # 設定輸出檔案
        output_csv = self.database_dir / "ingredient_database.csv"

        if target_vegetable:
            # 處理指定蔬菜
            print(f"🎯 目標蔬菜：{target_vegetable}")
            vegetables_to_process = [target_vegetable]
        else:
            # 處理所有蔬菜
            vegetables = self.get_available_vegetables()
            if not vegetables:
                print("❌ 找不到任何可處理的蔬菜資料")
                return

            print(f"🔍 找到 {len(vegetables)} 種蔬菜：{', '.join(vegetables[:5])}{'...' if len(vegetables) > 5 else ''}")

            # 詢問是否處理所有蔬菜
            choice = input(f"\n是否要處理所有 {len(vegetables)} 種蔬菜的食材資料？(y/N)：").lower()
            if choice != 'y':
                print("🛑 取消批次處理")
                return

            vegetables_to_process = vegetables

        # 收集所有食材資料
        all_ingredient_data = []
        success_count = 0
        failed_vegetables = []

        print(f"\n📊 開始處理 {len(vegetables_to_process)} 種蔬菜的食材資料...")
        print("-" * 60)

        for vege_name in vegetables_to_process:
            ingredient_data = self.process_vegetable_ingredients(vege_name)
            if ingredient_data:
                all_ingredient_data.extend(ingredient_data)
                success_count += 1
            else:
                failed_vegetables.append(vege_name)

        # 儲存合併後的食材資料
        if all_ingredient_data:
            result_df = pd.DataFrame(all_ingredient_data)
            result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

            print("\n" + "=" * 60)
            print("📊 食材資料庫建立完成")
            print("=" * 60)
            print(f"✅ 成功處理：{success_count} 種蔬菜")
            print(f"❌ 處理失敗：{len(failed_vegetables)} 種蔬菜")
            print(f"📝 總食材筆數：{len(all_ingredient_data)} 筆食材")
            print(f"💾 資料庫檔案：{output_csv}")

            if failed_vegetables:
                print(f"⚠️  失敗清單：{', '.join(failed_vegetables)}")

            # 顯示食材統計
            ingredient_counts = result_df['ingredient'].value_counts()
            print(f"\n📈 最常見的食材（前10名）：")
            for ingredient, count in ingredient_counts.head(10).items():
                print(f"  {ingredient}: {count} 次")

            # 顯示資料預覽
            print(f"\n📋 資料預覽（前5筆）：")
            for i, (_, row) in enumerate(result_df.head(5).iterrows()):
                quantity_unit = f"{row['quantity']} {row['unit']}" if row['quantity'] and row['unit'] else row['quantity'] or ""
                print(f"  {i+1}. 食譜ID:{row['id']} - {row['ingredient']} ({quantity_unit})")

        else:
            print("\n❌ 沒有成功處理任何食材資料")

    def process_vegetable_steps(self, vege_name):
        """處理單一蔬菜的食譜步驟資料，返回處理後的步驟資料"""
        print(f"🥬 處理蔬菜步驟：{vege_name}")

        # 設定檔案路徑
        vege_dir = self.cleaned_csv_dir / vege_name
        input_csv = vege_dir / f"{vege_name}_清理後食譜.csv"

        if not input_csv.exists():
            print(f"⚠️  找不到檔案：{input_csv}")
            return []

        try:
            # 讀取原始資料
            df = pd.read_csv(input_csv, encoding='utf-8-sig')
            print(f"  📊 讀取到 {len(df)} 筆食譜資料")

            # 檢查必要欄位是否存在
            required_fields = ["id", "steps"]
            missing_fields = [field for field in required_fields if field not in df.columns]
            if missing_fields:
                print(f"  ❌ 缺少必要欄位：{missing_fields}")
                return []

            # 建立步驟資料
            step_data = []
            for _, row in df.iterrows():
                recipe_id = row["id"]
                steps_str = row["steps"]

                if pd.isna(steps_str) or not steps_str:
                    continue

                # 分割步驟（假設用 " | " 分隔）
                steps = steps_str.split(" | ") if isinstance(steps_str, str) else []

                for step_no, description in enumerate(steps, 1):
                    if description.strip():  # 跳過空步驟
                        # 清理步驟描述：移除換行符號，避免 CSV 格式錯誤
                        cleaned_description = description.strip().replace('\n', ' ').replace('\r', ' ')
                        # 移除多餘的空格
                        cleaned_description = ' '.join(cleaned_description.split())

                        record = {
                            "id": recipe_id,
                            "description": cleaned_description,
                            "step_no": step_no
                        }
                        step_data.append(record)

            print(f"  ✅ 成功處理 {len(step_data)} 筆步驟資料")
            return step_data

        except Exception as e:
            print(f"  ❌ 處理 {vege_name} 步驟時發生錯誤：{e}")
            return []



    def create_recipe_steps_database(self, target_vegetable=None):
        """建立食譜步驟資料庫"""
        print("📝 食譜步驟資料庫建立工具")
        print("=" * 60)

        # 設定輸出檔案
        output_csv = self.database_dir / "recipe_steps_database.csv"

        if target_vegetable:
            vegetables_to_process = [target_vegetable]
        else:
            vegetables = self.get_available_vegetables()
            if not vegetables:
                print("❌ 找不到任何可處理的蔬菜資料")
                return

            print(f"🔍 找到 {len(vegetables)} 種蔬菜：{', '.join(vegetables[:5])}{'...' if len(vegetables) > 5 else ''}")
            choice = input(f"\n是否要處理所有 {len(vegetables)} 種蔬菜的步驟資料？(y/N)：").lower()
            if choice != 'y':
                print("🛑 取消批次處理")
                return
            vegetables_to_process = vegetables

        # 收集所有步驟資料
        all_step_data = []
        success_count = 0
        failed_vegetables = []

        print(f"\n📊 開始處理 {len(vegetables_to_process)} 種蔬菜的步驟資料...")
        print("-" * 60)

        for vege_name in vegetables_to_process:
            step_data = self.process_vegetable_steps(vege_name)
            if step_data:
                all_step_data.extend(step_data)
                success_count += 1
            else:
                failed_vegetables.append(vege_name)

        # 儲存合併後的步驟資料
        if all_step_data:
            result_df = pd.DataFrame(all_step_data)
            result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

            print("\n" + "=" * 60)
            print("📊 食譜步驟資料庫建立完成")
            print("=" * 60)
            print(f"✅ 成功處理：{success_count} 種蔬菜")
            print(f"❌ 處理失敗：{len(failed_vegetables)} 種蔬菜")
            print(f"📝 總步驟筆數：{len(all_step_data)} 筆步驟")
            print(f"💾 資料庫檔案：{output_csv}")

            if failed_vegetables:
                print(f"⚠️  失敗清單：{', '.join(failed_vegetables)}")

            # 顯示步驟統計
            step_counts = result_df.groupby('id')['step_no'].max()
            print(f"\n📈 步驟數統計：")
            print(f"  平均步驟數：{step_counts.mean():.1f}")
            print(f"  最多步驟數：{step_counts.max()}")
            print(f"  最少步驟數：{step_counts.min()}")

            # 顯示資料預覽
            print(f"\n📋 資料預覽（前5筆）：")
            for i, (_, row) in enumerate(result_df.head(5).iterrows()):
                print(f"  {i+1}. 食譜ID:{row['id']} 步驟{row['step_no']}: {row['description'][:50]}...")
        else:
            print("\n❌ 沒有成功處理任何步驟資料")


    
    def run(self, target_vegetable=None):
        """執行資料庫建立作業"""
        print("🗄️  食譜資料庫建立工具")
        print("=" * 60)

        # 設定輸出檔案
        output_csv = self.database_dir / "main_recipe_database.csv"

        if target_vegetable:
            # 處理指定蔬菜
            print(f"🎯 目標蔬菜：{target_vegetable}")
            vegetables_to_process = [target_vegetable]
        else:
            # 處理所有蔬菜
            vegetables = self.get_available_vegetables()
            if not vegetables:
                print("❌ 找不到任何可處理的蔬菜資料")
                return

            print(f"🔍 找到 {len(vegetables)} 種蔬菜：{', '.join(vegetables[:5])}{'...' if len(vegetables) > 5 else ''}")

            # 詢問是否處理所有蔬菜
            choice = input(f"\n是否要處理所有 {len(vegetables)} 種蔬菜？(y/N)：").lower()
            if choice != 'y':
                print("🛑 取消批次處理")
                return

            vegetables_to_process = vegetables

        # 收集所有資料
        all_data = []
        success_count = 0
        failed_vegetables = []

        print(f"\n📊 開始處理 {len(vegetables_to_process)} 種蔬菜...")
        print("-" * 60)

        for vege_name in vegetables_to_process:
            vege_data = self.process_vegetable(vege_name)
            if vege_data:
                all_data.extend(vege_data)
                success_count += 1
            else:
                failed_vegetables.append(vege_name)

        # 儲存合併後的資料
        if all_data:
            result_df = pd.DataFrame(all_data)
            result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')

            print("\n" + "=" * 60)
            print("📊 資料庫建立完成")
            print("=" * 60)
            print(f"✅ 成功處理：{success_count} 種蔬菜")
            print(f"❌ 處理失敗：{len(failed_vegetables)} 種蔬菜")
            print(f"📝 總資料筆數：{len(all_data)} 筆食譜")
            print(f"💾 資料庫檔案：{output_csv}")

            if failed_vegetables:
                print(f"⚠️  失敗清單：{', '.join(failed_vegetables)}")

            # 顯示各蔬菜的資料統計
            vege_counts = result_df['vege_name'].value_counts()
            print(f"\n� 各蔬菜資料統計：")
            for vege, count in vege_counts.head(10).items():
                print(f"  {vege}: {count} 筆")
            if len(vege_counts) > 10:
                print(f"  ... 還有 {len(vege_counts) - 10} 種蔬菜")

            # 顯示資料預覽
            print(f"\n📋 資料預覽（前5筆）：")
            for i, (_, row) in enumerate(result_df.head(5).iterrows()):
                print(f"  {i+1}. [{row['vege_name']}] {row['recipe']} (ID: {row['id']})")

        else:
            print("\n❌ 沒有成功處理任何資料")


def main():
    try:
        creator = DatabaseCreator()

        # 檢查命令列參數
        if len(sys.argv) > 1:
            command = sys.argv[1]
            target_vegetable = sys.argv[2] if len(sys.argv) > 2 else None

            if command == "ingredient":
                creator.create_ingredient_database(target_vegetable)
            elif command == "steps":
                creator.create_recipe_steps_database(target_vegetable)
            else:
                # 建立主食譜資料庫
                creator.run(command)
        else:
            # 互動式選擇
            print("🗄️  資料庫建立工具")
            print("=" * 50)
            print("請選擇要建立的資料庫：")
            print("1. 主食譜資料庫 (main_recipe_database.csv)")
            print("2. 食材資料庫 (ingredient_database.csv)")
            print("3. 食譜步驟資料庫 (recipe_steps_database.csv)")
            print("4. 建立所有資料庫")

            choice = input("\n請輸入選項 (1/2/3/4)：").strip()

            if choice == "1":
                creator.run()
            elif choice == "2":
                creator.create_ingredient_database()
            elif choice == "3":
                creator.create_recipe_steps_database()
            elif choice == "4":
                print("\n🚀 建立所有資料庫...")
                creator.run()
                print("\n" + "="*60)
                creator.create_ingredient_database()
                print("\n" + "="*60)
                creator.create_recipe_steps_database()
            else:
                print("❌ 無效的選項")

    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
