#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
食譜處理流水線主控制腳本
串接所有處理步驟：爬取 → 清理 → 向量化 → 相似度分析

使用方法：
1. 完整流水線：python run_pipeline.py
2. 指定菜名：python run_pipeline.py 小白菜
3. 從特定步驟開始：python run_pipeline.py --start-from clean
4. 只執行特定步驟：python run_pipeline.py --only crawl
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path


class RecipePipeline:
    def __init__(self, vegetable_name=None):
        self.base_dir = Path(__file__).parent
        self.project_root = self.base_dir.parent
        self.vegetable_name = vegetable_name
        
        # 定義各步驟的腳本檔案
        self.scripts = {
            'crawl': 'crawl_icook_recipes.py',
            'clean': 'clean_recipe_csv_0720.py', 
            'generate': 'generate_documents.py',
            'analyze': 'check_duplicates.py'
        }
        
        # 步驟描述
        self.step_descriptions = {
            'crawl': '🕷️  爬取食譜資料',
            'clean': '🧹 清理食譜資料',
            'generate': '📄 生成向量化文件',
            'analyze': '📊 執行相似度分析'
        }
    
    def print_banner(self):
        """顯示程式橫幅"""
        print("=" * 60)
        print("🍳 食譜處理流水線 Recipe Processing Pipeline")
        print("=" * 60)
        if self.vegetable_name:
            print(f"🥬 目標菜名：{self.vegetable_name}")
        print()
    
    def check_script_exists(self, script_name):
        """檢查腳本檔案是否存在"""
        script_path = self.base_dir / script_name
        return script_path.exists()
    
    def run_script(self, step_name, script_name, args=None):
        """執行指定的腳本"""
        print(f"\n{self.step_descriptions[step_name]}")
        print("-" * 40)
        
        if not self.check_script_exists(script_name):
            print(f"❌ 找不到腳本檔案：{script_name}")
            return False
        
        # 建構命令
        cmd = [sys.executable, script_name]
        if args:
            cmd.extend(args)
        
        print(f"🚀 執行命令：{' '.join(cmd)}")
        
        try:
            # 在 scripts 目錄下執行
            result = subprocess.run(
                cmd, 
                cwd=self.base_dir,
                capture_output=False,  # 讓輸出直接顯示在控制台
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {self.step_descriptions[step_name]} 完成")
                return True
            else:
                print(f"❌ {self.step_descriptions[step_name]} 失敗 (返回碼: {result.returncode})")
                return False
                
        except Exception as e:
            print(f"❌ 執行 {script_name} 時發生錯誤：{e}")
            return False
    
    def run_crawl(self):
        """執行爬蟲步驟"""
        args = [self.vegetable_name] if self.vegetable_name else []
        return self.run_script('crawl', self.scripts['crawl'], args)
    
    def run_clean(self):
        """執行清理步驟"""
        # clean_recipe_csv_0720.py 會自動處理檔案
        return self.run_script('clean', self.scripts['clean'])
    
    def run_generate(self):
        """執行文件生成步驟"""
        # generate_documents.py 會自動處理所有菜名資料夾
        return self.run_script('generate', self.scripts['generate'])
    
    def run_analyze(self):
        """執行相似度分析步驟"""
        # check_duplicates.py 會自動處理所有菜名資料夾
        return self.run_script('analyze', self.scripts['analyze'])
    
    def run_full_pipeline(self):
        """執行完整流水線"""
        self.print_banner()
        
        steps = [
            ('crawl', self.run_crawl),
            ('clean', self.run_clean), 
            ('generate', self.run_generate),
            ('analyze', self.run_analyze)
        ]
        
        start_time = time.time()
        failed_steps = []
        
        for step_name, step_func in steps:
            print(f"\n{'='*20} 步驟 {len([s for s in steps if s[0] <= step_name])}/{len(steps)} {'='*20}")
            
            if not step_func():
                failed_steps.append(step_name)
                print(f"\n⚠️  步驟 '{step_name}' 失敗，是否繼續執行後續步驟？")
                choice = input("輸入 'y' 繼續，其他任意鍵退出：").lower()
                if choice != 'y':
                    break
        
        # 顯示總結
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🎯 流水線執行完成")
        print("=" * 60)
        print(f"⏱️  總執行時間：{duration:.2f} 秒")
        
        if failed_steps:
            print(f"❌ 失敗的步驟：{', '.join(failed_steps)}")
        else:
            print("✅ 所有步驟執行成功！")
        
        return len(failed_steps) == 0
    
    def run_from_step(self, start_step):
        """從指定步驟開始執行"""
        step_order = ['crawl', 'clean', 'generate', 'analyze']
        
        if start_step not in step_order:
            print(f"❌ 無效的起始步驟：{start_step}")
            print(f"可用步驟：{', '.join(step_order)}")
            return False
        
        start_index = step_order.index(start_step)
        
        self.print_banner()
        print(f"🚀 從步驟 '{start_step}' 開始執行")
        
        step_functions = {
            'crawl': self.run_crawl,
            'clean': self.run_clean,
            'generate': self.run_generate, 
            'analyze': self.run_analyze
        }
        
        for step in step_order[start_index:]:
            print(f"\n{'='*20} 執行步驟：{step} {'='*20}")
            if not step_functions[step]():
                print(f"❌ 步驟 '{step}' 失敗")
                return False
        
        print("\n✅ 所有步驟執行完成！")
        return True
    
    def run_single_step(self, step):
        """只執行單一步驟"""
        step_functions = {
            'crawl': self.run_crawl,
            'clean': self.run_clean,
            'generate': self.run_generate,
            'analyze': self.run_analyze
        }
        
        if step not in step_functions:
            print(f"❌ 無效的步驟：{step}")
            print(f"可用步驟：{', '.join(step_functions.keys())}")
            return False
        
        self.print_banner()
        print(f"🎯 只執行步驟：{step}")
        
        return step_functions[step]()


def main():
    parser = argparse.ArgumentParser(
        description="食譜處理流水線主控制腳本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  python run_pipeline.py                    # 執行完整流水線
  python run_pipeline.py 小白菜             # 指定菜名執行完整流水線
  python run_pipeline.py --start-from clean # 從清理步驟開始
  python run_pipeline.py --only crawl       # 只執行爬蟲步驟
        """
    )
    
    parser.add_argument('vegetable_name', nargs='?', help='要處理的菜名（可選）')
    parser.add_argument('--start-from', choices=['crawl', 'clean', 'generate', 'analyze'],
                       help='從指定步驟開始執行')
    parser.add_argument('--only', choices=['crawl', 'clean', 'generate', 'analyze'],
                       help='只執行指定的單一步驟')
    
    args = parser.parse_args()
    
    # 建立流水線實例
    pipeline = RecipePipeline(args.vegetable_name)
    
    try:
        if args.only:
            # 只執行單一步驟
            success = pipeline.run_single_step(args.only)
        elif args.start_from:
            # 從指定步驟開始
            success = pipeline.run_from_step(args.start_from)
        else:
            # 執行完整流水線
            success = pipeline.run_full_pipeline()
        
        # 設定退出碼
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  使用者中斷執行")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 執行過程中發生未預期的錯誤：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
