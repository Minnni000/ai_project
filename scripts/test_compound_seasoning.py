#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試複合調味料拆分功能
"""

# 從 clean_recipe_csv_0720.py 導入相關函數
import sys
import os
sys.path.append(os.path.dirname(__file__))

from clean_recipe_csv_0720 import parse_ingredient, split_seasoning_compounds

def test_compound_seasonings():
    test_cases = [
        "鹽巴白胡椒粉少許",
        "鹽巴白胡椒粉",
        "白胡椒粉少許",
        "鹽巴少許",
        "醬油香油適量",
        "糖鹽巴",
    ]
    
    print("🧪 測試複合調味料拆分功能")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📝 測試：'{test_case}'")
        
        # 測試拆分功能
        compound_parts = split_seasoning_compounds(test_case.replace("少許", "").replace("適量", "").strip())
        print(f"  拆分結果：{compound_parts}")
        
        # 測試解析功能
        parsed = parse_ingredient(test_case)
        print(f"  解析結果：{parsed}")

if __name__ == "__main__":
    test_compound_seasonings()
