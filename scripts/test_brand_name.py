#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試品牌名稱中包含中文數字的食材解析
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from clean_recipe_csv_0720 import parse_ingredient

def test_brand_name():
    """測試品牌名稱中包含中文數字的解析"""
    test_cases = [
        {
            "input": "小磨坊蒜香九層塔適量",
            "expected": {
                "name": "小磨坊蒜香九層塔",
                "quantity": "適量",
                "unit": None
            }
        },
        {
            "input": "九層塔一把",  # 這個應該正常解析
            "expected": {
                "name": "九層塔",
                "quantity": 1,
                "unit": "把"
            }
        },
        {
            "input": "統一三合一咖啡少許",
            "expected": {
                "name": "統一三合一咖啡",
                "quantity": "少許",
                "unit": None
            }
        },
        {
            "input": "蔥三根",  # 這個應該正常解析
            "expected": {
                "name": "蔥",
                "quantity": 3,
                "unit": "根"
            }
        },
        {
            "input": "味全高鮮味精適量",
            "expected": {
                "name": "味全高鮮味精",
                "quantity": "適量",
                "unit": None
            }
        }
    ]
    
    print("🧪 測試品牌名稱中包含中文數字的食材解析")
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
        print("🎉 品牌名稱解析修正成功！")
    else:
        print("⚠️  品牌名稱解析仍有問題")
    
    return all_passed

if __name__ == "__main__":
    test_brand_name()
