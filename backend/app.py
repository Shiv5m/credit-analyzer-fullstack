from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import re
import json
import os

app = Flask(__name__)
CORS(app)

with open(os.path.join(os.path.dirname(__file__), "merchant_category_db.json")) as f:
    MERCHANT_DB = json.load(f)

def clean_merchant(merchant):
    merchant = merchant.lower()
    merchant = re.sub(r'[^a-z0-9 ]+', '', merchant)
    merchant = re.sub(r'\s+', ' ', merchant).strip()
    return merchant

def categorize_by_merchant(merchant):
    merchant = clean_merchant(merchant)
    if merchant in MERCHANT_DB:
        return MERCHANT_DB[merchant]
    for key in MERCHANT_DB:
        if key in merchant:
            return MERCHANT_DB[key]
    return "Others"

EXCLUDE_KEYWORDS = ["credit", "cr", "payment", "statement", "refund", "adjustment", "reversal"]

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

            for line in lines:
                line_clean = line.encode("ascii", "ignore").decode().strip().lower()
                if "american express" in line_clean and "credit card" in line_clean:
                    return line.strip()
                if "credit card" in line_clean and len(line.strip()) <= 100:
                    return line.strip()

            full_text = "\n".join(lines).lower()
            if "american express" in full_text:
                return "American Express Credit Card"
            elif "hdfc" in full_text:
                return "HDFC Bank Credit Card"
            elif "axis" in full_text:
                return "Axis Bank Credit Card"
            elif "icici" in full_text:
                return "ICICI Bank Credit Card"
    except Exception:
        pass
    return "Unknown"

def parse(text, card_name="Unknown"):
    txns = []
    pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)")
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if match:
            date, merchant, amount = match.groups()
            if is_expense(merchant):
                txns.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "category": categorize_by_merchant(merchant),
                    "amount": float(amount.replace(",", "")),
                    "card": card_name
                })
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
