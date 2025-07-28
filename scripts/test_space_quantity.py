#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試空格+模糊量詞的食材解析
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from clean_recipe_csv_0720 import parse_ingredient

def test_space_quantity():
    """測試空格+模糊量詞的解析"""
    test_cases = [
        {
            "input": "薑絲 小撮",
            "expected": {
                "name": "薑絲",
                "quantity": "小撮",
                "unit": None
            }
        },
        {
            "input": "蒜末 少許",
            "expected": {
                "name": "蒜末",
                "quantity": "少許",
                "unit": None
            }
        },
        {
            "input": "胡椒粉 適量",
            "expected": {
                "name": "胡椒粉",
                "quantity": "適量",
                "unit": None
            }
        },
        {
            "input": "鹽 一撮",
            "expected": {
                "name": "鹽",
                "quantity": "一撮",
                "unit": None
            }
        }
    ]
    
    print("🧪 測試空格+模糊量詞食材解析")
    print("=" * 60)
    
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
    
    print("=" * 60)
    if all_passed:
        print("🎉 空格+模糊量詞解析修正成功！")
    else:
        print("⚠️  空格+模糊量詞解析仍有問題")
    
    return all_passed

if __name__ == "__main__":
    test_space_quantity()
