import React, { useState } from "react";
import { utils, writeFile } from "xlsx";

export default function App() {
  const [pdfFiles, setPdfFiles] = useState([]);
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);

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
      if (data.transactions) allTxns.push(...data.transactions);
    }

    const grouped = {};
    allTxns.forEach(txn => {
      grouped[txn.category] = (grouped[txn.category] || 0) + txn.amount;
    });

    setSummary(grouped);
    setTransactions(allTxns);
  };

  const downloadCSV = () => {
    const ws = utils.json_to_sheet(transactions);
    const wb = utils.book_new();
    utils.book_append_sheet(wb, ws, "Report");
    writeFile(wb, "credit-card-report.xlsx");
  };

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Credit Card Spend Analyzer</h1>

      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={(e) => setPdfFiles([...e.target.files])}
      />

      <button
        onClick={analyzeFile}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Analyze
      </button>

      {summary && (
        <>
          <h2 className="text-xl font-semibold mt-6 mb-2">Summary (Category-wise)</h2>
          <table className="w-full border mb-6">
            <thead>
              <tr>
                <th className="border p-2">Category</th>
                <th className="border p-2">Amount (₹)</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(summary).map(([cat, amt]) => (
                <tr key={cat}>
                  <td className="border p-2">{cat}</td>
                  <td className="border p-2">₹{amt.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex justify-end mb-2">
            <button
              onClick={downloadCSV}
              className="px-4 py-2 bg-green-600 text-white rounded"
            >
              Download CSV
            </button>
          </div>

          <h2 className="text-xl font-semibold mt-4 mb-2">All Transactions</h2>
          <table className="w-full border text-sm">
            <thead>
              <tr>
                <th className="border p-2">Date</th>
                <th className="border p-2">Merchant</th>
                <th className="border p-2">Category</th>
                <th className="border p-2">Amount (₹)</th>
                <th className="border p-2">Card</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((txn, idx) => (
                <tr key={idx}>
                  <td className="border p-2">{txn.date}</td>
                  <td className="border p-2">{txn.merchant}</td>
                  <td className="border p-2">{txn.category}</td>
                  <td className="border p-2">₹{txn.amount.toFixed(2)}</td>
                  <td className="border p-2">{txn.card}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
