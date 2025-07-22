#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修正後的 parse_ingredient 函數
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from clean_recipe_csv_0720 import parse_ingredient

def test_parse_ingredients():
    test_cases = [
        ("香油少許", {"name": "香油", "quantity": "少許", "unit": None}),
        ("鹽1/2小匙", {"name": "鹽", "quantity": 0.5, "unit": "小匙"}),
        ("白胡椒粉少許", {"name": "白胡椒粉", "quantity": "少許", "unit": None}),
        ("糖少許", {"name": "糖", "quantity": "少許", "unit": None}),
        ("米酒少許", {"name": "米酒", "quantity": "少許", "unit": None}),
        ("蒜末少許", {"name": "蒜末", "quantity": "少許", "unit": None}),
        ("鹽巴白胡椒粉少許", {"name": "鹽巴", "quantity": "少許", "unit": None})  # 這個會在後處理階段拆分
    ]

    print("🧪 測試 parse_ingredient 函數修正")
    print("=" * 80)

    all_passed = True
    for test_input, expected in test_cases:
        result = parse_ingredient(test_input)
        passed = result == expected
        status = "✅ PASS" if passed else "❌ FAIL"

        print(f"{status} '{test_input}'")
        print(f"  期望: {expected}")
        print(f"  實際: {result}")

        if not passed:
            all_passed = False
        print()

    print("=" * 80)
    if all_passed:
        print("🎉 所有測試通過！")
    else:
        print("⚠️  有測試失敗，需要進一步調整")

if __name__ == "__main__":
    test_parse_ingredients()
