#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試全形斜線的食材解析
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from clean_recipe_csv_0720 import parse_ingredient

def test_fullwidth_slash():
    """測試全形斜線的解析"""
    test_case = {
        "input": "鹽1／8茶匙",  # 全形斜線
        "expected": {
            "name": "鹽",
            "quantity": 0.125,
            "unit": "茶匙"
        }
    }
    
    print("🧪 測試全形斜線食材解析")
    print("=" * 50)
    
    result = parse_ingredient(test_case["input"])
    expected = test_case["expected"]
    
    # 檢查是否匹配
    passed = (
        result["name"] == expected["name"] and
        result["quantity"] == expected["quantity"] and
        result["unit"] == expected["unit"]
    )
    
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} 測試: '{test_case['input']}'")
    print(f"  期望: {expected}")
    print(f"  實際: {result}")
    
    if passed:
        print("\n🎉 全形斜線解析修正成功！")
    else:
        print("\n⚠️  全形斜線解析仍有問題")
    
    return passed

if __name__ == "__main__":
    test_fullwidth_slash()
