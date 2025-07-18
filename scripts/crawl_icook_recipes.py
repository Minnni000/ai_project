import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random
import csv
import os

# 設定 headers 與根資料夾
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
base_url = "https://icook.tw"
image_root = r"D:\AIPE\aipe_project\image"
raw_csv_root = r"D:\AIPE\aipe_project\raw_csv"
os.makedirs(image_root, exist_ok=True)
os.makedirs(raw_csv_root, exist_ok=True)

def get_search_results(keyword: str, max_count: int = 20) -> list:
    results = []
    page = 1

    while len(results) < max_count:
        url = f"{base_url}/search/{keyword}?page={page}"
        print(f"🔄 讀取第 {page} 頁：{url}")
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        cards = soup.select("a.browse-recipe-link")
        if not cards:
            break

        for card in cards:
            recipe = {}
            recipe_name_tag = card.select_one("h2.browse-recipe-name")
            preview_ingredient_tag = card.select_one("p.browse-recipe-content-ingredient")
            article = card.select_one("article.browse-recipe-card")
            recipe_id = article.get("data-recipe-id") if article else ""
            img_tag = card.select_one("img.browse-recipe-cover-img")
            href = card.get("href")

            if recipe_name_tag and href and recipe_id:
                recipe["id"] = recipe_id
                recipe["name"] = recipe_name_tag.get_text(strip=True)
                recipe["url"] = urljoin(base_url, href)
                recipe["preview_ingredients"] = preview_ingredient_tag.get_text(strip=True).replace("食材：", "") if preview_ingredient_tag else ""
                img_url = img_tag.get("data-src") or img_tag.get("src") if img_tag else ""
                if img_url and "/w:200/" in img_url:
                    img_url = img_url.replace("/w:200/", "/")
                recipe["img_url"] = img_url
                if recipe["id"] not in [r["id"] for r in results]:
                    results.append(recipe)

            if len(results) >= max_count:
                break

        page += 1
        time.sleep(random.uniform(1, 1.5))

    return results

def get_recipe_details(recipe_url: str):
    resp = requests.get(recipe_url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    ingredients = []
    items = soup.select("li.ingredient")
    for li in items:
        name_tag = li.select_one(".ingredient-name")
        unit_tag = li.select_one(".ingredient-unit")
        name = name_tag.get_text(strip=True) if name_tag else ""
        unit = unit_tag.get_text(strip=True) if unit_tag else ""
        if name:
            ingredients.append(f"{name}{unit}")

    steps = []
    step_tags = soup.select("p.recipe-step-description-content")
    for step in step_tags:
        step_text = step.get_text(strip=True)
        if step_text:
            steps.append(step_text)

    return ingredients, steps

def download_image(url: str, path: str) -> str:
    if not url or url.startswith("data:image") or not url.startswith("http"):
        print(f"⚠️ 跳過無效圖片網址：{url}")
        return None

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        with open(path, "wb") as f:
            f.write(resp.content)
        print(f"✅ 圖片已下載：{path}")
        return path
    except Exception as e:
        print(f"⚠️ 無法下載圖片：{url}，錯誤：{e}")
        return None

def save_to_csv(data_list: list, filename: str):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_ALL)
        writer.writerow(["id", "食譜名稱", "網址", "預覽食材", "詳細食材", "做法", "圖片相對路徑"])
        for item in data_list:
            writer.writerow([
                item["id"],
                item["name"],
                item["url"],
                item["preview_ingredients"],
                ", ".join(item["ingredients"]),
                " / ".join(item["steps"]),
                item.get("image_path", "")
            ])
    print(f"\n✅ 已儲存 {len(data_list)} 筆資料到 {filename}")

def main(keywords: list[str]):
    for keyword in keywords:
        print(f"\n============================\n🔍 關鍵字：{keyword}")
        image_folder = os.path.join(image_root, keyword)
        os.makedirs(image_folder, exist_ok=True)

        results = get_search_results(keyword, max_count=50)
        print(f"共取得 {len(results)} 筆食譜")

        data_to_save = []

        for i, recipe in enumerate(results, 1):
            print(f"🍽 第 {i} 筆：{recipe['name']}")
            filename_safe = recipe["name"].replace(" ", "_").replace("/", "_")
            image_filename = f"{recipe['id']}_{filename_safe}.jpg"
            image_path = os.path.join(image_folder, image_filename)
            rel_path = os.path.relpath(image_path, start=image_root)
            recipe["image_path"] = rel_path

            download_image(recipe["img_url"], image_path)

            try:
                ingredients, steps = get_recipe_details(recipe["url"])
                recipe["ingredients"] = ingredients
                recipe["steps"] = steps
            except Exception as e:
                print(f"⚠️ 抓詳細資料失敗：{e}")
                recipe["ingredients"] = []
                recipe["steps"] = []

            data_to_save.append(recipe)
            print("-" * 40)
            time.sleep(random.uniform(1, 2))

        csv_filename = os.path.join(raw_csv_root, f"{keyword}_食譜資料.csv")
        save_to_csv(data_to_save, csv_filename)




if __name__ == "__main__":
    keywords = ["小白菜"]  # ✅ 自訂你的搜尋關鍵字清單
    main(keywords)

    # ,"青江菜", "大白菜", "油菜", "大陸妹", "龍鬚菜", "芹菜", "紅鳳菜", "紅蘿蔔", "芋頭", "山藥", "蓮藕", "地瓜葉", "牛番茄", "花椰菜", "苦瓜", "冬瓜", "大黃瓜", "小黃瓜", "青椒", "四季豆(敏豆)", "秋葵", "水蓮", "娃娃菜", "蒜苗", "蘆筍", "紅蔥頭", "玉米", "香菜", "蘿蔓"
