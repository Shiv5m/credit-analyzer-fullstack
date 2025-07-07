from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import re
import json
import os
import joblib

app = Flask(__name__)
CORS(app)

# Load keyword-based rules
with open(os.path.join(os.path.dirname(__file__), "merchant_keywords.json")) as f:
    MERCHANT_DB = json.load(f)

# Load ML fallback model
model_path = os.path.join(os.path.dirname(__file__), "merchant_classifier_model.pkl")
ML_MODEL = joblib.load(model_path)

MONTHS = ("january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december")

def clean_merchant(merchant):
    return re.sub(r'[^a-z0-9 ]+', '', merchant.lower()).strip()

def categorize_by_merchant(merchant):
    merchant_clean = clean_merchant(merchant)
    for category, keywords in MERCHANT_DB.items():
        for keyword in keywords:
            if keyword in merchant_clean:
                return category
    # fallback to ML model
    try:
        return ML_MODEL.predict([merchant])[0]
    except:
        return "Others"

EXCLUDE_KEYWORDS = ["credit", "cr", "payment", "statement", "refund", "adjustment", "reversal", "received"]

def is_expense(merchant):
    return not any(kw in merchant.lower() for kw in EXCLUDE_KEYWORDS)

def extract_text(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())

def detect_card_name(pdf_file):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            first_page = pdf.pages[0]
            lines = (first_page.extract_text() or "").splitlines()
            for line in lines[:5]:
                if "credit card" in line.lower():
                    return line.replace("Statement", "").strip()
    except Exception:
        pass
    return "Unknown"

def parse(text, card_name="Unknown"):
    txns = []
    lines = text.splitlines()

    date_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)")
    for line in lines:
        line = line.strip()

        m1 = date_pattern.match(line)
        if m1:
            date, merchant, amount = m1.groups()
            if is_expense(merchant):
                txns.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "category": categorize_by_merchant(merchant),
                    "amount": float(amount.replace(",", "")),
                    "card": card_name
                })
            continue

        tokens = line.split()
        if len(tokens) >= 4 and tokens[0].lower() in MONTHS:
            try:
                month = tokens[0].capitalize()
                day = tokens[1].zfill(2)
                amount_str = tokens[-1].replace(",", "")
                float(amount_str)
                merchant = " ".join(tokens[2:-1]).strip()
                if is_expense(merchant):
                    date = f"{day}/{str(MONTHS.index(month.lower())+1).zfill(2)}/2025"
                    txns.append({
                        "date": date,
                        "merchant": merchant,
                        "category": categorize_by_merchant(merchant),
                        "amount": float(amount_str),
                        "card": card_name
                    })
            except:
                continue

    return txns

def summarize(txns):
    summary = {}
    for txn in txns:
        summary[txn["category"]] = summary.get(txn["category"], 0) + txn["amount"]
    return summary

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    f = request.files['file']
    text = extract_text(f)
    f.seek(0)
    card = detect_card_name(f)
    txns = parse(text, card)
    return jsonify({"summary": summarize(txns), "transactions": txns})

@app.route('/resolve-merchants', methods=['POST'])
def resolve_merchants():
    data = request.get_json()
    merchants = data.get("merchants", [])
    suggestions = []

    for merchant in merchants:
        category = categorize_by_merchant(merchant)
        source = "https://www.google.com/search?q=" + merchant.replace(" ", "+")
        suggestions.append({
            "merchant": merchant,
            "category": category,
            "source": source
        })

    return jsonify({"suggestions": suggestions})


import os
import json

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


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
import pandas as pd

@app.route('/retrain-model', methods=['POST'])
def retrain_model():
    from pathlib import Path

    # Load manual labels
    label_path = Path(__file__).parent / "merchant_labels.json"
    manual_samples = []
    if label_path.exists():
        with open(label_path) as f:
            manual_data = json.load(f)
            manual_samples = [{"merchant": k, "category": v} for k, v in manual_data.items()]

    # Load keywords as base training
    keyword_path = Path(__file__).parent / "merchant_keywords.json"
    with open(keyword_path) as f:
        keyword_map = json.load(f)

    synthetic_samples = []
    import random
    for category, keywords in keyword_map.items():
        for kw in keywords:
            for _ in range(3):
                merchant = f"{kw} {random.choice(['pvt ltd', 'india', 'bangalore', ''])}".strip()
                synthetic_samples.append({"merchant": merchant.title(), "category": category})

    df = pd.DataFrame(synthetic_samples + manual_samples)
    if df.empty:
        return jsonify({"error": "No data to train"}), 400

    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
        ("clf", LogisticRegression(max_iter=500))
    ])
    model.fit(df["merchant"], df["category"])
    model_path = Path(__file__).parent / "merchant_classifier_model.pkl"
    joblib.dump(model, model_path)

    return jsonify({"message": "Model retrained", "samples": len(df)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
