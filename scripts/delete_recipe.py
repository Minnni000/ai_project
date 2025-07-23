#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根據 delete_list.txt 中的 ID 刪除食譜資料和圖片檔案

功能：
1. 從 delete_list.txt 讀取要刪除的食譜 ID
2. 從 cleaned_csv 目錄下的所有 CSV 檔案中刪除對應的食譜記錄
3. 從 image 目錄中刪除對應的圖片檔案
4. 更新相關的 JSON 檔案

使用方法：
python delete_recipe.py
"""

import os
import sys
import csv
import json
import glob
from pathlib import Path


class RecipeDeleter:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.project_root = self.base_dir.parent
        self.cleaned_csv_dir = self.project_root / "cleaned_csv"
        self.image_dir = self.project_root / "image"
        self.delete_list_file = self.base_dir / "delete_list.txt"

        self.deleted_count = 0
        self.deleted_images = 0
        self.processed_files = []

    def load_delete_list(self):
        """從 delete_list.txt 讀取要刪除的 ID 清單"""
        if not self.delete_list_file.exists():
            print(f"❌ 找不到檔案：{self.delete_list_file}")
            return []

        delete_ids = []
        try:
            with open(self.delete_list_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    # 跳過空行和註解行
                    if not line or line.startswith("#"):
                        continue

                    # 驗證 ID 格式（應該是數字）
                    if line.isdigit():
                        delete_ids.append(line)
                    else:
                        print(f"⚠️  第 {line_num} 行格式錯誤，跳過：{line}")

            print(f"📋 從 delete_list.txt 讀取到 {len(delete_ids)} 個要刪除的 ID")
            return delete_ids

        except Exception as e:
            print(f"❌ 讀取 delete_list.txt 時發生錯誤：{e}")
            return []

    def delete_from_csv(self, csv_file_path, delete_ids):
        """從 CSV 檔案中刪除指定 ID 的記錄"""
        if not os.path.exists(str(csv_file_path)):
            return 0

        deleted_count = 0
        temp_file = str(csv_file_path) + ".tmp"

        try:
            with open(str(csv_file_path), "r", encoding="utf-8-sig") as infile, open(
                temp_file, "w", newline="", encoding="utf-8-sig"
            ) as outfile:

                reader = csv.DictReader(infile)
                writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
                writer.writeheader()

                for row in reader:
                    if row["id"] in delete_ids:
                        deleted_count += 1
                        print(f"  🗑️  刪除食譜：{row['id']} - {row['name']}")
                    else:
                        writer.writerow(row)

            # 替換原檔案
            os.replace(temp_file, str(csv_file_path))
            return deleted_count

        except Exception as e:
            print(f"❌ 處理 CSV 檔案時發生錯誤：{e}")
            # 清理臨時檔案
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return 0

    def delete_from_json(self, json_file_path, delete_ids):
        """從 JSON 檔案中刪除指定 ID 的記錄"""
        if not os.path.exists(str(json_file_path)):
            return 0

        deleted_count = 0

        try:
            with open(str(json_file_path), "r", encoding="utf-8") as infile:
                recipes = json.load(infile)

            original_count = len(recipes)
            filtered_recipes = [
                recipe for recipe in recipes if recipe["id"] not in delete_ids
            ]
            deleted_count = original_count - len(filtered_recipes)

            # 只有在實際刪除記錄時才更新檔案
            if deleted_count > 0:
                with open(str(json_file_path), "w", encoding="utf-8") as outfile:
                    json.dump(filtered_recipes, outfile, ensure_ascii=False, indent=2)
                print(f"  📝 JSON 檔案已更新，刪除 {deleted_count} 筆記錄")

            return deleted_count

        except Exception as e:
            print(f"❌ 處理 JSON 檔案時發生錯誤：{e}")
            return 0

    def delete_images(self, delete_ids):
        """刪除對應的圖片檔案"""
        deleted_images = 0

        if not self.image_dir.exists():
            print(f"⚠️  圖片目錄不存在：{self.image_dir}")
            return 0

        # 搜尋所有可能的圖片檔案格式
        image_extensions = ["jpg", "jpeg", "png", "gif", "webp"]

        for delete_id in delete_ids:
            found_image = False

            # 在所有子目錄中搜尋以 ID 開頭的圖片檔案（格式：ID_食譜名稱.副檔名）
            for ext in image_extensions:
                # 搜尋模式：ID_*.副檔名
                pattern = f"**/{delete_id}_*.{ext}"
                matching_files = list(self.image_dir.glob(pattern))

                for image_file in matching_files:
                    try:
                        image_file.unlink()
                        print(f"  🖼️  刪除圖片：{image_file.name}")
                        deleted_images += 1
                        found_image = True
                    except Exception as e:
                        print(f"❌ 刪除圖片失敗 {image_file}：{e}")

                # 也搜尋只有 ID 的檔案（向後相容）
                pattern_simple = f"**/{delete_id}.{ext}"
                matching_files_simple = list(self.image_dir.glob(pattern_simple))

                for image_file in matching_files_simple:
                    try:
                        image_file.unlink()
                        print(f"  🖼️  刪除圖片：{image_file.name}")
                        deleted_images += 1
                        found_image = True
                    except Exception as e:
                        print(f"❌ 刪除圖片失敗 {image_file}：{e}")

            if not found_image:
                print(f"  ⚠️  找不到 ID {delete_id} 對應的圖片檔案")

        return deleted_images

    def process_vegetable_folder(self, vegetable_dir, delete_ids):
        """處理單一蔬菜資料夾"""
        vegetable_name = vegetable_dir.name
        print(f"\n🥬 處理蔬菜資料夾：{vegetable_name}")

        folder_deleted_count = 0

        # 處理 CSV 檔案
        csv_file = vegetable_dir / f"{vegetable_name}_清理後食譜.csv"
        if csv_file.exists():
            deleted = self.delete_from_csv(csv_file, delete_ids)
            folder_deleted_count += deleted
            if deleted > 0:
                self.processed_files.append(str(csv_file))

        # 處理 JSON 檔案
        json_file = vegetable_dir / f"{vegetable_name}_清理後食譜.json"
        if json_file.exists():
            deleted = self.delete_from_json(json_file, delete_ids)
            if deleted > 0:
                self.processed_files.append(str(json_file))

        # 處理 recipe_documents.csv 檔案
        documents_csv_file = vegetable_dir / f"{vegetable_name}_recipe_documents.csv"
        if documents_csv_file.exists():
            deleted = self.delete_from_csv(documents_csv_file, delete_ids)
            if deleted > 0:
                self.processed_files.append(str(documents_csv_file))

        return folder_deleted_count

    def run(self):
        """執行刪除作業"""
        print("🗑️  食譜刪除工具")
        print("=" * 50)

        # 讀取要刪除的 ID 清單
        delete_ids = self.load_delete_list()
        if not delete_ids:
            print("❌ 沒有要刪除的 ID")
            return

        print(f"🎯 要刪除的 ID：{', '.join(delete_ids)}")

        # 確認操作
        choice = input(f"\n⚠️  確定要刪除這 {len(delete_ids)} 個食譜嗎？(y/N)：").lower()
        if choice != "y":
            print("🛑 取消刪除操作")
            return

        print("\n🚀 開始執行刪除作業...")

        # 處理所有蔬菜資料夾，但只處理包含要刪除 ID 的資料夾
        if self.cleaned_csv_dir.exists():
            vegetable_dirs = [d for d in self.cleaned_csv_dir.iterdir() if d.is_dir()]

            for vegetable_dir in vegetable_dirs:
                # 先檢查這個資料夾是否包含要刪除的 ID
                csv_file = vegetable_dir / f"{vegetable_dir.name}_清理後食譜.csv"
                if not csv_file.exists():
                    continue

                # 檢查 CSV 檔案中是否包含要刪除的 ID
                has_target_ids = False
                try:
                    with open(str(csv_file), "r", encoding="utf-8-sig") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row["id"] in delete_ids:
                                has_target_ids = True
                                break
                except Exception:
                    continue

                # 只處理包含目標 ID 的資料夾
                if has_target_ids:
                    deleted = self.process_vegetable_folder(vegetable_dir, delete_ids)
                    self.deleted_count += deleted
        else:
            print(f"⚠️  找不到 cleaned_csv 目錄：{self.cleaned_csv_dir}")

        # 刪除圖片檔案（保持原有邏輯）
        self.delete_images(delete_ids)

        # 顯示結果
        self.print_summary()

    def print_summary(self):
        # 顯示結果摘要
        print("\n" + "=" * 50)
        print("📊 刪除作業完成")
        print("=" * 50)
        print(f"🗑️  刪除的食譜記錄：{self.deleted_count} 筆")
        print(f"🖼️  刪除的圖片檔案：{self.deleted_images} 個")
        print(f"📁 處理的檔案數量：{len(self.processed_files)}")

        if self.processed_files:
            print(f"\n📝 已更新的檔案：")
            for file_path in self.processed_files:
                print(f"  - {file_path}")


def main():
    try:
        deleter = RecipeDeleter()
        deleter.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
