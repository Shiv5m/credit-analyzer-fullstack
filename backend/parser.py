import re
import json
import pdfplumber

with open("merchant_category_db.json", "r") as f:
    MERCHANT_CATEGORY_DB = json.load(f)

def get_category(merchant):
    merchant_clean = re.sub(r"[^a-z0-9 ]", "", merchant.lower())
    for keyword, category in MERCHANT_CATEGORY_DB.items():
        if keyword in merchant_clean:
            return category
    return "Others"

def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(file_bytes) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def detect_bank(text):
    text_lower = text.lower()
    if "axis bank" in text_lower:
        return "Axis"
    elif "american express" in text_lower:
        return "Amex"
    elif "hdfc bank" in text_lower:
        return "HDFC"
    elif "icici bank" in text_lower:
        return "ICICI"
    return "Unknown"

def parse_transactions(text, bank):
    lines = text.splitlines()
    transactions = []

    for line in lines:
        if bank == "Axis":
            match = re.match(r"(\d{2}-[A-Za-z]{3})\s+(.*?)\s+(\d+\.\d{2})", line)
            if match:
                date, merchant, amount = match.groups()
                transactions.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "amount": float(amount),
                })
        elif bank == "Amex":
            match = re.match(r"(\d{2}/\d{2})\s+(.*?)\s+(INR|Rs\.?)\s*([\d,]+\.\d{2})", line)
            if match:
                date, merchant, _, amount = match.groups()
                transactions.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "amount": float(amount.replace(",", "")),
                })
        elif bank == "HDFC":
            match = re.match(r"(\d{2}/\d{2}/\d{4})\s+(.*?)\s+INR\s*([\d,]+\.\d{2})", line)
            if match:
                date, merchant, amount = match.groups()
                transactions.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "amount": float(amount.replace(",", "")),
                })
        elif bank == "ICICI":
            match = re.match(r"(\d{2}-[A-Za-z]{3}-\d{4})\s+(.*?)\s+(INR|Rs\.?)\s*([\d,]+\.\d{2})", line)
            if match:
                date, merchant, _, amount = match.groups()
                transactions.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "amount": float(amount.replace(",", "")),
                })

    return transactions

def analyze_pdf(file_bytes):
    text = extract_text_from_pdf(file_bytes)
    bank = detect_bank(text)
    txns = parse_transactions(text, bank)

    for txn in txns:
        txn["category"] = get_category(txn["merchant"])

    summary = {}
    for txn in txns:
        summary[txn["category"]] = summary.get(txn["category"], 0) + txn["amount"]

    return {
        "bank": bank,
        "summary": summary,
        "transactions": txns,
    }
