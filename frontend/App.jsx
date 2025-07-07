import React, { useState } from "react";

export default function App() {
  const [pdfFiles, setPdfFiles] = useState([]);
  const [summary, setSummary] = useState(null);

  const analyzeFile = async () => {
    let allTxns = [];

    for (const file of pdfFiles) {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(import.meta.env.VITE_API_URL + "/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      allTxns = allTxns.concat(data.transactions || []);
    }

    const grouped = {};
    allTxns.forEach(txn => {
      grouped[txn.category] = (grouped[txn.category] || 0) + txn.amount;
    });

    setSummary(grouped);
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Credit Card Spend Analyzer</h1>
      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={(e) => setPdfFiles([...e.target.files])}
      />
      <button onClick={analyzeFile} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded">
        Analyze
      </button>

      {summary && (
        <table className="mt-6 w-full border">
          <thead><tr><th className="border p-2">Category</th><th className="border p-2">Amount (₹)</th></tr></thead>
          <tbody>
            {Object.entries(summary).map(([cat, amt]) => (
              <tr key={cat}><td className="border p-2">{cat}</td><td className="border p-2">₹{amt.toFixed(2)}</td></tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
