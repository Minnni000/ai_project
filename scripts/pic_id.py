#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將所有蔬菜資料夾中的圖片重新命名並複製到統一資料夾
原始：461995_水蓮的脆爽小撇步！水蓮炒豆芽.jpg
新名：461995.jpg
"""

import os
import shutil
from pathlib import Path

# 設定路徑
script_dir = Path(__file__).parent
project_root = script_dir.parent
image_root = project_root / "image"
output_dir = image_root / "all_pic"

# 建立輸出目錄
output_dir.mkdir(exist_ok=True)

print("🔍 開始處理圖片檔案...")
print(f"📁 來源目錄：{image_root}")
print(f"📁 輸出目錄：{output_dir}")

processed_count = 0
skipped_count = 0

# 遍歷 image 目錄下的所有子資料夾
for vegetable_folder in image_root.iterdir():
    if vegetable_folder.is_dir() and vegetable_folder.name != "all_pic":
        print(f"\n🥬 處理蔬菜資料夾：{vegetable_folder.name}")

        # 處理該資料夾中的所有圖片
        for filename in vegetable_folder.iterdir():
            if filename.suffix.lower() == ".jpg" and "_" in filename.name:
                # 提取 ID 部分
                number_part = filename.name.split("_")[0]
                new_filename = f"{number_part}.jpg"

                # 設定來源和目標路徑
                source_path = filename
                target_path = output_dir / new_filename

                try:
                    # 複製並重新命名檔案
                    shutil.copy2(source_path, target_path)
                    print(f"  ✅ {filename.name} → {new_filename}")
                    processed_count += 1
                except Exception as e:
                    print(f"  ❌ 處理失敗 {filename.name}：{e}")
                    skipped_count += 1
            elif filename.suffix.lower() == ".jpg":
                print(f"  ⚠️  跳過（無底線）：{filename.name}")
                skipped_count += 1

print(f"\n🎉 處理完成！")
print(f"✅ 成功處理：{processed_count} 個檔案")
print(f"⚠️  跳過檔案：{skipped_count} 個檔案")
print(f"📁 所有圖片已儲存至：{output_dir}")
