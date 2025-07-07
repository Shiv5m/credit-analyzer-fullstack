
from flask import Flask, request, jsonify
import os
import json
import joblib
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pandas as pd


def categorize_merchant(merchant_name, keywords, model=None):
    merchant_lower = merchant_name.lower()

    for category, words in keywords.items():
        for word in words:
            if word.lower() in merchant_lower:
                return category

    # ML fallback
    if model:
        try:
            probas = model.predict_proba([merchant_name])[0]
            categories = model.classes_
            max_idx = probas.argmax()
            if probas[max_idx] >= 0.7:
                return categories[max_idx]
        except:
            pass

    return "Others"

app = Flask(__name__)

LABEL_PATH = os.path.join(os.path.dirname(__file__), "merchant_labels.json")

@app.route('/label-merchant', methods=['POST'])
def label_merchant():
    new_labels = request.get_json()
    if not isinstance(new_labels, dict):
        return jsonify({"error": "Invalid format"}), 400

    if os.path.exists(LABEL_PATH):
        with open(LABEL_PATH, "r") as f:
            labels = json.load(f)
    else:
        labels = {}

    labels.update(new_labels)
    with open(LABEL_PATH, "w") as f:
        json.dump(labels, f, indent=2)

    return jsonify({"message": "Labels saved successfully"})

@app.route('/retrain-model', methods=['POST'])
def retrain_model():
    label_path = Path(__file__).parent / "merchant_labels.json"
    if not label_path.exists():
        return jsonify({"error": "No labels found"}), 400

    with open(label_path) as f:
        manual_data = json.load(f)

    data = [{"merchant": k, "category": v} for k, v in manual_data.items()]
    df = pd.DataFrame(data)

    if df.empty:
        return jsonify({"error": "No training data"}), 400

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
        ("clf", LogisticRegression(max_iter=500))
    ])
    model.fit(df["merchant"], df["category"])

    model_path = Path(__file__).parent / "merchant_classifier_model.pkl"
    joblib.dump(model, model_path)

    return jsonify({"message": "Model retrained", "samples": len(df)})

if __name__ == "__main__":
    app.run(debug=True)
