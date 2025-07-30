#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試括號移除功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from clean_recipe_csv_0720 import parse_ingredient

def test_bracket_removal():
    """測試括號移除功能"""
    test_cases = [
        {
            "input": "七味醬1茶匙（5ml）",
            "expected": {
                "name": "七味醬",
                "quantity": 1.0,
                "unit": "茶匙"
            }
        },
        {
            "input": "鰹魚調味露2茶匙（10ml）",
            "expected": {
                "name": "鰹魚調味露",
                "quantity": 2.0,
                "unit": "茶匙"
            }
        },
        {
            "input": "香醋3茶匙（15ml）",
            "expected": {
                "name": "香醋",
                "quantity": 3.0,
                "unit": "茶匙"
            }
        },
        {
            "input": "S&B 生蒜泥醬1茶匙（5ml）",
            "expected": {
                "name": "S&B 生蒜泥醬",
                "quantity": 1.0,
                "unit": "茶匙"
            }
        },
        {
            "input": "香油3茶匙（15ml）",
            "expected": {
                "name": "香油",
                "quantity": 3.0,
                "unit": "茶匙"
            }
        },
        {
            "input": "鮭魚1片(270g)",  # 這個應該保持原有邏輯
            "expected": {
                "name": "鮭魚(270g)",
                "quantity": 1.0,
                "unit": "片"
            }
        }
    ]
    
    print("🧪 測試括號移除功能")
    print("=" * 70)
    
    all_passed = True
    for i, case in enumerate(test_cases, 1):
        result = parse_ingredient(case["input"])
        expected = case["expected"]
        
        # 檢查是否匹配
        passed = (
            result["name"] == expected["name"] and
            result["quantity"] == expected["quantity"] and
            result["unit"] == expected["unit"]
        )
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} 測試 {i}: '{case['input']}'")
        print(f"  期望: {expected}")
        print(f"  實際: {result}")
        
        if not passed:
            all_passed = False
        print()
    
    print("=" * 70)
    if all_passed:
        print("🎉 括號移除功能修正成功！")
    else:
        print("⚠️  括號移除功能仍有問題")
    
    return all_passed

if __name__ == "__main__":
    test_bracket_removal()
