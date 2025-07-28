#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試中文數字和範圍數字的食材解析
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from clean_recipe_csv_0720 import parse_ingredient

def test_chinese_patterns():
    """測試中文數字和範圍數字的解析"""
    test_cases = [
        {
            "input": "九層塔一把",
            "expected": {
                "name": "九層塔",
                "quantity": 1,
                "unit": "把"
            }
        },
        {
            "input": "薑絲一小撮",
            "expected": {
                "name": "薑絲",
                "quantity": 1,
                "unit": "小撮"
            }
        },
        {
            "input": "水1～2大匙",
            "expected": {
                "name": "水",
                "quantity": "1～2",
                "unit": "大匙"
            }
        },
        {
            "input": "蔥三根",
            "expected": {
                "name": "蔥",
                "quantity": 3,
                "unit": "根"
            }
        },
        {
            "input": "油1~2茶匙",  # 半形波浪號
            "expected": {
                "name": "油",
                "quantity": "1~2",
                "unit": "茶匙"
            }
        }
    ]
    
    print("🧪 測試中文數字和範圍數字食材解析")
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
        print("🎉 中文數字和範圍數字解析修正成功！")
    else:
        print("⚠️  中文數字和範圍數字解析仍有問題")
    
    return all_passed

if __name__ == "__main__":
    test_chinese_patterns()
