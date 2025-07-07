import re
import json
import fitz  # PyMuPDF

with open("merchant_category_db.json", "r") as f:
    MERCHANT_CATEGORY_DB = json.load(f)

def extract_text_from_pdf(file_stream):
    text = ""
    with fitz.open(stream=file_stream.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def detect_bank(text):
    text = text.lower()
    if "axis bank" in text:
        return "Axis"
    elif "american express" in text:
        return "Amex"
    elif "hdfc bank" in text:
        return "HDFC"
    elif "icici bank" in text:
        return "ICICI"
    else:
        return "Unknown"

def get_category_simple(merchant):
    for keyword, category in MERCHANT_CATEGORY_DB.items():
        if keyword.lower() in merchant.lower():
            return category
    return "Others"

def parse_transactions(text, bank):
    lines = text.splitlines()
    transactions = []

    for line in lines:
        if bank == "Axis":
            match = re.match(r"(\\d{2}-[A-Za-z]{3})\\s+(.*?)\\s+(\\d+\\.\\d{2})", line)
            if match:
                date, merchant, amount = match.groups()
                transactions.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "amount": float(amount),
                })

        elif bank == "Amex":
            match = re.match(r"(\\d{2}/\\d{2})\\s+(.*?)\\s+(INR|Rs\\.?)[\\s]*([\\d,]+\\.\\d{2})", line)
            if match:
                date, merchant, _, amount = match.groups()
                amount = float(amount.replace(",", ""))
                transactions.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "amount": amount,
                })

        elif bank == "HDFC":
            match = re.match(r"(\\d{2}/\\d{2}/\\d{4})\\s+(.*?)\\s+INR\\s*([\\d,]+\\.\\d{2})", line)
            if match:
                date, merchant, amount = match.groups()
                amount = float(amount.replace(",", ""))
                transactions.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "amount": amount,
                })

        elif bank == "ICICI":
            match = re.match(r"(\\d{2}-[A-Za-z]{3}-\\d{4})\\s+(.*?)\\s+(INR|Rs\\.?)[\\s]*([\\d,]+\\.\\d{2})", line)
            if match:
                date, merchant, _, amount = match.groups()
                amount = float(amount.replace(",", ""))
                transactions.append({
                    "date": date,
                    "merchant": merchant.strip(),
                    "amount": amount,
                })

    return transactions

def analyze_pdf(file_stream):
    text = extract_text_from_pdf(file_stream)
    bank = detect_bank(text)
    txns = parse_transactions(text, bank)

    for txn in txns:
        txn["category"] = get_category_simple(txn["merchant"])

    summary = {}
    for txn in txns:
        if txn["category"] != "Others" and txn["amount"] > 0:
            summary[txn["category"]] = summary.get(txn["category"], 0) + txn["amount"]
        elif txn["category"] == "Others":
            summary["Others"] = summary.get("Others", 0) + txn["amount"]

    return {
        "bank": bank,
        "summary": summary,
        "transactions": txns,
    }
