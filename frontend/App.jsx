import React, { useState } from "react";

export default function CreditAnalyzer() {
  const [pdfFiles, setPdfFiles] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = (e) => {
    setPdfFiles([...e.target.files]);
  };

  const analyzeFile = async () => {
    setLoading(true);
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
          const taggedTxns = data.transactions.map((txn) => ({
            ...txn,
            bank: data.bank || "Unknown",
          }));
          allTxns = allTxns.concat(taggedTxns);
        }
      } catch (error) {
        console.error("Failed to analyze file:", file.name, error);
      }
    }

    const summary = {};
    allTxns.forEach((txn) => {
      summary[txn.category] = (summary[txn.category] || 0) + txn.amount;
    });

    setAnalysis({ summary, transactions: allTxns });
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-3xl">
        <h1 className="text-4xl font-bold mb-8 text-center text-blue-800">
          Credit Card Spend Analyzer
        </h1>

        <div className="bg-white rounded-lg shadow-md p-8 mb-10 border border-gray-200 text-center">
          <label className="block text-lg font-medium mb-3">
            Upload one or more Credit Card Statements (PDF)
          </label>
          <input
            type="file"
            accept="application/pdf"
            multiple
            onChange={handleUpload}
            className="mx-auto text-sm border border-gray-300 rounded px-4 py-2 mb-4"
          />
          <br />
          <button
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded disabled:opacity-50"
            onClick={analyzeFile}
            disabled={!pdfFiles.length || loading}
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>

        {analysis && (
          <>
            <div className="bg-white rounded-lg shadow-sm p-6 mb-8 border border-gray-200">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800 text-center">
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
                      <td className="p-3 border-b">₹{amount.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800 text-center">
                Transactions
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="border-b p-3">Date</th>
                      <th className="border-b p-3">Merchant</th>
                      <th className="border-b p-3">Amount</th>
                      <th className="border-b p-3">Category</th>
                      <th className="border-b p-3">Bank</th>
                    </tr>
                  </thead>
                  <tbody>
                    {analysis.transactions.map((txn, i) => (
                      <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                        <td className="p-3 border-b">{txn.date}</td>
                        <td className="p-3 border-b">{txn.merchant}</td>
                        <td className="p-3 border-b">₹{txn.amount}</td>
                        <td className="p-3 border-b">{txn.category}</td>
                        <td className="p-3 border-b">{txn.bank}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
