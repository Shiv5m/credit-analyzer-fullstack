from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import re
import json
import os

app = Flask(__name__)
CORS(app)

# Load category mappings
with open(os.path.join(os.path.dirname(__file__), "merchant_category_db.json")) as f:
    MERCHANT_DB = json.load(f)

EXCLUDE_KEYWORDS = [
    "credit", "cr", "payment", "received", "statement credit", 
    "auto debit", "autopay", "reversal", "adjustment", "reward", "loyalty"
]

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

def detect_bank(text):
    if "HDFC Bank Credit Card" in text:
        return "HDFC"
    elif "American Express" in text:
        return "AMEX"
    elif "ICICI Bank Credit Card" in text or "ICICI Bank" in text:
        return "ICICI"
    elif "Axis Bank" in text:
        return "AXIS"
    return "UNKNOWN"

def categorize_by_merchant(merchant):
    m = merchant.lower()
    for keyword, category in MERCHANT_DB.items():
        if keyword in m:
            return category
    return "Others"

def is_expense(merchant):
    return not any(kw in merchant.lower() for kw in EXCLUDE_KEYWORDS)

def parse_axis(text):
    txns = []
    txn_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+[A-Z &]+?\s+([\d,]+\.\d{2})\s+Dr")
    for line in text.splitlines():
        match = txn_pattern.match(line.strip())
        if match:
            date, merchant, amount = match.groups()
            if is_expense(merchant):
                txns.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "category": categorize_by_merchant(merchant),
                    "amount": float(amount.replace(",", ""))
                })
    return txns

def parse_amex(text):
    txns = []
    txn_pattern = re.compile(r"([A-Za-z]+ \d{2})\s+(.+?)\s+([\d,]+\.\d{2})$")
    for line in text.splitlines():
        match = txn_pattern.match(line.strip())
        if match:
            date, merchant, amount = match.groups()
            if is_expense(merchant):
                txns.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "category": categorize_by_merchant(merchant),
                    "amount": float(amount.replace(",", ""))
                })
    return txns

def parse_hdfc(text):
    txns = []
    txn_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,]+\.\d{2})$")
    for line in text.splitlines():
        match = txn_pattern.match(line.strip())
        if match:
            date, merchant, amount = match.groups()
            if is_expense(merchant):
                txns.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "category": categorize_by_merchant(merchant),
                    "amount": float(amount.replace(",", ""))
                })
    return txns

def parse_icici(text):
    txns = []
    txn_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,]+\.\d{2})$")
    for line in text.splitlines():
        match = txn_pattern.match(line.strip())
        if match:
            date, merchant, amount = match.groups()
            if is_expense(merchant):
                txns.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "category": categorize_by_merchant(merchant),
                    "amount": float(amount.replace(",", ""))
                })
    return txns

def summarize(txns):
    summary = {}
    for txn in txns:
        cat = txn["category"]
        summary[cat] = summary.get(cat, 0) + txn["amount"]
    return summary

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    text = extract_text_from_pdf(file)
    bank = detect_bank(text)

    if bank == "HDFC":
        txns = parse_hdfc(text)
    elif bank == "ICICI":
        txns = parse_icici(text)
    elif bank == "AMEX":
        txns = parse_amex(text)
    elif bank == "AXIS":
        txns = parse_axis(text)
    else:
        return jsonify({"summary": {}, "transactions": [], "bank": "Unknown"})

    summary = summarize(txns)
    return jsonify({"summary": summary, "transactions": txns, "bank": bank})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
