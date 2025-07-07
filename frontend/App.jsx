import React, { useState } from "react";

export default function CreditAnalyzer() {
  const [pdfFile, setPdfFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const dummyResult = {
    summary: {
      Food: 3200,
      Travel: 1500,
      Utilities: 2000,
      Shopping: 4500,
      Others: 800,
    },
    transactions: [
      { date: "04-Jun", merchant: "Swiggy", amount: 578, category: "Food" },
      { date: "05-Jun", merchant: "Amazon", amount: 1200, category: "Shopping" },
      { date: "07-Jun", merchant: "Uber", amount: 320, category: "Travel" },
    ],
  };

  const handleUpload = (e) => {
    setPdfFile(e.target.files[0]);
  };

  const analyzeFile = () => {
    setLoading(true);
    setTimeout(() => {
      setAnalysis(dummyResult);
      setLoading(false);
    }, 1500); // simulate delay
  };

  return (
    <div className="max-w-6xl mx-auto p-6 font-sans">
      <h1 className="text-4xl font-bold mb-6 text-center text-blue-700">
        Credit Card Spend Analyzer
      </h1>

      <div className="bg-white rounded shadow p-6 mb-8 border border-gray-200">
        <label className="block text-lg font-medium mb-2">
          Upload your Credit Card Statement (PDF)
        </label>
        <input
          type="file"
          accept="application/pdf"
          onChange={handleUpload}
          className="block w-full text-sm border border-gray-300 rounded p-2"
        />
        <button
          className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded disabled:opacity-50"
          onClick={analyzeFile}
          disabled={!pdfFile || loading}
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {analysis && (
        <>
          <div className="bg-white rounded shadow p-6 mb-6 border border-gray-200">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              Spending Summary
            </h2>
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border-b p-3">Category</th>
                  <th className="border-b p-3">Amount (₹)</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(analysis.summary).map(([category, amount], i) => (
                  <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                    <td className="p-3 border-b font-medium">{category}</td>
                    <td className="p-3 border-b">₹{amount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="bg-white rounded shadow p-6 border border-gray-200">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              Transactions
            </h2>
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-100">
                  <th className="border-b p-3">Date</th>
                  <th className="border-b p-3">Merchant</th>
                  <th className="border-b p-3">Amount</th>
                  <th className="border-b p-3">Category</th>
                </tr>
              </thead>
              <tbody>
                {analysis.transactions.map((txn, i) => (
                  <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                    <td className="p-3 border-b">{txn.date}</td>
                    <td className="p-3 border-b">{txn.merchant}</td>
                    <td className="p-3 border-b">₹{txn.amount}</td>
                    <td className="p-3 border-b">{txn.category}</td>
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
