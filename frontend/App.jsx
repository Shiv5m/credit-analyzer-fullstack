// Full App.jsx with analysis, categorization, CSV export, and resolve-merchants
import React, { useState } from "react";
import { utils, writeFile } from "xlsx";

export default function App() {
  const [pdfFiles, setPdfFiles] = useState([]);
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [suggested, setSuggested] = useState([]);
  const [loadingResolve, setLoadingResolve] = useState(false);

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
    allTxns.forEach((txn) => {
      grouped[txn.category] = (grouped[txn.category] || 0) + txn.amount;
    });

    setSummary(grouped);
    setTransactions(allTxns);
    setSuggested([]);
  };

  const downloadCSV = () => {
    const ws = utils.json_to_sheet(transactions);
    const wb = utils.book_new();
    utils.book_append_sheet(wb, ws, "Report");
    writeFile(wb, "credit-card-report.xlsx");
  };

  const resolveMerchants = async () => {
    const others = transactions.filter((txn) => txn.category === "Others");
    if (!others.length) return;

    setLoadingResolve(true);

    const res = await fetch(import.meta.env.VITE_API_URL + "/resolve-merchants", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ merchants: others.map((txn) => txn.merchant) }),
    });

    const data = await res.json();
    setSuggested(data.suggestions || []);
    setLoadingResolve(false);
  };

  return (
    <div className="p-4 max-w-5xl mx-auto">
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

          <div className="flex gap-2 justify-end mb-2">
            <button
              onClick={resolveMerchants}
              className="px-4 py-2 bg-yellow-600 text-white rounded"
              disabled={loadingResolve}
            >
              {loadingResolve ? "Checking..." : "Recheck Unknown Merchants"}
            </button>

            <button
              onClick={downloadCSV}
              className="px-4 py-2 bg-green-600 text-white rounded"
            >
              Download CSV
            </button>
          </div>

          <h2 className="text-xl font-semibold mt-4 mb-2">All Transactions</h2>
          <table className="w-full border text-sm mb-6">
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

      {suggested.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-bold mb-2">Suggestions for "Others" Merchants</h2>
          <table className="w-full border text-sm">
            <thead>
              <tr>
                <th className="border p-2">Merchant</th>
                <th className="border p-2">Suggested Category</th>
                <th className="border p-2">Source</th>
              </tr>
            </thead>
            <tbody>
              {suggested.map((sug, i) => (
                <tr key={i}>
                  <td className="border p-2">{sug.merchant}</td>
                  <td className="border p-2">{sug.category}</td>
                  <td className="border p-2">
                    <a
                      href={sug.source}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 underline"
                    >
                      Link
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
