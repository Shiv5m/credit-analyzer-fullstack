
from flask import Flask, request, jsonify
import os
import json
import pdfplumber
from pathlib import Path

app = Flask(__name__)

def categorize_merchant(merchant_name, keywords):
    merchant_lower = merchant_name.lower()
    for category, words in keywords.items():
        for word in words:
            if word.lower() in merchant_lower:
                return category
    return "Others"

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["file"]
    filename = file.filename
    card_name = filename.replace("Statement", "").replace(".pdf", "").strip()

    temp_path = "/tmp/temp.pdf"
    file.save(temp_path)

    with pdfplumber.open(temp_path) as pdf:
        text = "\n".join([
            page.extract_text() for page in pdf.pages if page.extract_text()
        ])

    os.remove(temp_path)

    lines = text.splitlines()
    transactions = []

    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 3:
            try:
                amount = float(parts[-1].replace(",", "").replace("₹", ""))
                date = parts[0]
                merchant = " ".join(parts[1:-1])
                transactions.append({
                    "date": date,
                    "merchant": merchant,
                    "amount": amount,
                    "card": card_name
                })
            except:
                continue

    # Load keywords
    keyword_path = Path(__file__).parent / "merchant_keywords.json"
    if not keyword_path.exists():
        return jsonify({"error": "merchant_keywords.json not found"}), 500

    with open(keyword_path) as f:
        keyword_map = json.load(f)

    # Assign categories
    for txn in transactions:
        txn["category"] = categorize_merchant(txn["merchant"], keyword_map)

    summary = {}
    for txn in transactions:
        summary[txn["category"]] = summary.get(txn["category"], 0) + txn["amount"]

    return jsonify({
        "summary": summary,
        "transactions": transactions
    })

@app.route('/label-merchant', methods=['POST'])
def label_merchant():
    LABEL_PATH = Path(__file__).parent / "merchant_labels.json"
    new_labels = request.get_json()
    if not isinstance(new_labels, dict):
        return jsonify({"error": "Invalid format"}), 400

    if LABEL_PATH.exists():
        with open(LABEL_PATH, "r") as f:
            labels = json.load(f)
    else:
        labels = {}

    labels.update(new_labels)
    with open(LABEL_PATH, "w") as f:
        json.dump(labels, f, indent=2)

    return jsonify({"message": "Labels saved successfully"})

if __name__ == "__main__":
    app.run(debug=True)
