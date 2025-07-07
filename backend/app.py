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

MONTHS = ("january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december")

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
            if len(lines) >= 3:
                line3 = lines[2].strip()
                if "credit card" in line3.lower():
                    return line3.replace("Statement", "").strip()
            for line in lines:
                l = line.encode("ascii", "ignore").decode().strip().lower()
                if "credit card" in l:
                    return line.strip().replace("Statement", "").strip()
            return "Unknown"
    except Exception:
        return "Unknown"

def parse(text, card_name="Unknown"):
    txns = []
    lines = text.splitlines()

    date_pattern = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)")
    alt_pattern = re.compile(r"^([A-Za-z]+)\s+(\d{1,2})\s+(.+?)\s+(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$")

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

        m2 = alt_pattern.match(line)
        if m2:
            month, day, merchant, amount = m2.groups()
            if month.lower() in MONTHS and is_expense(merchant):
                date = f"{day.zfill(2)}/{str(list(MONTHS).index(month.lower())+1).zfill(2)}/2025"
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
