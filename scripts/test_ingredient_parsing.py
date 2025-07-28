#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試食材解析修正效果
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from clean_recipe_csv_0720 import parse_ingredient

def test_specific_cases():
    """測試特定的問題案例"""
    test_cases = [
        {
            "input": "鮭魚1片(270g)",
            "expected": {
                "name": "鮭魚(270g)",
                "quantity": 1.0,
                "unit": "片"
            }
        },
        {
            "input": "檸檬1/4顆",
            "expected": {
                "name": "檸檬",
                "quantity": 0.25,
                "unit": "顆"
            }
        },
        {
            "input": "小磨坊-蒜香九層塔1/8茶匙",
            "expected": {
                "name": "小磨坊-蒜香九層塔",
                "quantity": 0.125,
                "unit": "茶匙"
            }
        },
        {
            "input": "小磨坊-蒜香九層塔1/4茶匙",
            "expected": {
                "name": "小磨坊-蒜香九層塔",
                "quantity": 0.25,
                "unit": "茶匙"
            }
        },
        {
            "input": "鹽1/2茶匙",
            "expected": {
                "name": "鹽",
                "quantity": 0.5,
                "unit": "茶匙"
            }
        },
        {
            "input": "米酒1茶匙",
            "expected": {
                "name": "米酒",
                "quantity": 1.0,
                "unit": "茶匙"
            }
        }
    ]
    
    print("🧪 測試食材解析修正效果")
    print("=" * 80)
    
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
    
    print("=" * 80)
    if all_passed:
        print("🎉 所有測試通過！食材解析修正成功！")
    else:
        print("⚠️  有測試失敗，需要進一步調整")
    
    return all_passed

if __name__ == "__main__":
    test_specific_cases()
