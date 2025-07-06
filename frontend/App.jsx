import React, { useState } from "react";

export default function CreditAnalyzer() {
  const [pdfFiles, setPdfFiles] = useState([]);
  const [analysis, setAnalysis] = useState(null);

  const analyzeFile = async () => {
    let allTxns = [];

    for (const file of pdfFiles) {
      const formData = new FormData();
      formData.append("file", file);

      try {
        const res = await fetch(import.meta.env.VITE_API_URL + "/analyze", {
          method: "POST",
          body: formData,
        });

        const data = await res.json();
        if (data.transactions) {
          // tag each txn with its source bank
          const taggedTxns = data.transactions.map((txn) => ({
            ...txn,
            bank: data.bank || "Unknown",
          }));
          allTxns = allTxns.concat(taggedTxns);
        }
      } catch (error) {
        console.error("Failed to parse:", file.name, error);
      }
    }

    // Consolidate category totals
    const summary = {};
    allTxns.forEach((txn) => {
      summary[txn.category] = (summary[txn.category] || 0) + txn.amount;
    });

    setAnalysis({ summary, transactions: allTxns });
  };

  const downloadCSV = () => {
    if (!analysis?.transactions?.length) return;

    const headers = ["Date", "Merchant", "Amount", "Category", "Bank"];
    const rows = analysis.transactions.map((txn) => [
      txn.date,
      txn.merchant,
      txn.amount,
      txn.category,
      txn.bank,
    ]);

    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers, ...rows]
        .map((row) => row.map((cell) => `"${cell}"`).join(","))
        .join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.href = encodedUri;
    link.download = "credit_report.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="max-w-6xl mx-auto p-4 font-sans">
      <h1 className="text-3xl font-bold mb-6 text-center">Credit Card Spend Analyzer</h1>

      <div className="p-4 mb-6 border rounded shadow">
        <input
          type="file"
          accept="application/pdf"
          multiple
          onChange={(e) => setPdfFiles([...e.target.files])}
          className="block mb-4"
        />
        <button
          className="mr-4 px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
          onClick={analyzeFile}
          disabled={pdfFiles.length === 0}
        >
          Analyze
        </button>
        {analysis && analysis.transactions.length > 0 && (
          <button
            className="px-4 py-2 bg-green-600 text-white rounded"
            onClick={downloadCSV}
          >
            Download CSV
          </button>
        )}
      </div>

      {analysis && (
        <>
          {/* Summary Table */}
          <div className="mb-6 border rounded p-4 shadow">
            <h2 className="text-xl font-semibold mb-4">Category-wise Summary</h2>
            <table className="w-full text-left border-collapse">
              <thead>
                <tr>
                  <th className="border-b p-2">Category</th>
                  <th className="border-b p-2">Total Spend (₹)</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(analysis.summary).map(([category, total], i) => (
                  <tr key={i}>
                    <td className="p-2 border-b">{category}</td>
                    <td className="p-2 border-b">₹{total.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Transactions Table */}
          <div className="border rounded p-4 shadow">
            <h2 className="text-xl font-semibold mb-4">All Transactions</h2>
            <table className="w-full text-left border-collapse">
              <thead>
                <tr>
                  <th className="border-b p-2">Date</th>
                  <th className="border-b p-2">Merchant</th>
                  <th className="border-b p-2">Amount</th>
                  <th className="border-b p-2">Category</th>
                  <th className="border-b p-2">Bank</th>
                </tr>
              </thead>
              <tbody>
                {analysis.transactions.map((txn, i) => (
                  <tr key={i}>
                    <td className="p-2 border-b">{txn.date}</td>
                    <td className="p-2 border-b">{txn.merchant}</td>
                    <td className="p-2 border-b">₹{txn.amount}</td>
                    <td className="p-2 border-b">{txn.category}</td>
                    <td className="p-2 border-b">{txn.bank}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
