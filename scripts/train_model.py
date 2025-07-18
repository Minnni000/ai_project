import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 讀 JSON 資料
def load_data(json_path):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    return data

# 轉成訓練資料格式
def prepare_dataset(data):
    texts = []
    labels = []
    for item in data:
        texts.append(item['combined_text'])
        # 假設有label欄位，這裡用0/1示範。沒有的話可先隨便標或改成回歸問題
        labels.append(item.get('label', 0))  
    return texts, labels

def main():
    json_path = r"D:\AIPE\aipe_project\cleaned_csv\小白菜_清理後食譜.json"
    data = load_data(json_path)

    texts, labels = prepare_dataset(data)

    # 分割資料集
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )

    # TF-IDF 向量化
    vectorizer = TfidfVectorizer(max_features=5000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # 建立邏輯回歸模型
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    # 預測並評估
    y_pred = model.predict(X_test_vec)
    print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    main()
