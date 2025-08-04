import pandas as pd

# 讀取資料
main_recipe = pd.read_csv('main_recipe.csv')
ingredient = pd.read_csv('ingredient.csv')

# 找出重複的 id
duplicate_ids = main_recipe[main_recipe.duplicated(subset=['id'], keep=False)]['id'].unique()
print(f"\n找到 {len(duplicate_ids)} 個重複的 ID: {duplicate_ids}")

# 主食譜保留第一筆
main_recipe_clean = main_recipe.drop_duplicates(subset=['id'], keep='first')

# ingredient.csv：保留所有資料，只去掉完全重複的行
ingredient_clean = ingredient.drop_duplicates(subset=['recipe_id', 'ingredient', 'preview_tag'], keep='first')

# recipe_steps.csv：保留所有資料，只去掉完全重複的行
try:
    recipe_steps = pd.read_csv('recipe_steps.csv')
    print("recipe_steps.csv 讀取成功，共", len(recipe_steps), "筆")

    recipe_steps_clean = recipe_steps.drop_duplicates(subset=['recipe_id', 'step_no', 'description'], keep='first')
    recipe_steps_clean.to_csv('recipe_steps_clean.csv', index=False)
    print(f"清理 recipe_steps.csv: {len(recipe_steps)} -> {len(recipe_steps_clean)} 筆（去除完全重複步驟）")

except FileNotFoundError:
    print("找不到 recipe_steps.csv，跳過處理...")

# 儲存清理後檔案
main_recipe_clean.to_csv('main_recipe_clean.csv', index=False)
ingredient_clean.to_csv('ingredient_clean.csv', index=False)

print(f"清理 main_recipe.csv: {len(main_recipe)} -> {len(main_recipe_clean)} 筆")
print(f"清理 ingredient.csv: {len(ingredient)} -> {len(ingredient_clean)} 筆")
