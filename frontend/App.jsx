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

  const totalAmount = analysis
    ? analysis.transactions.reduce((sum, txn) => sum + txn.amount, 0)
    : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-100 to-blue-100 flex flex-col justify-between">
      {/* Header */}
      <header className="bg-white shadow py-4">
        <h1 className="text-3xl font-bold text-center text-blue-800">
          Credit Card Spend Analyzer
        </h1>
      </header>

      {/* Main Content */}
      <main className="flex-grow flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-4xl">
          <div className="bg-white rounded-2xl shadow-lg p-8 mb-10 border border-gray-300 text-center">
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
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-2.5 rounded shadow-md disabled:opacity-50"
              onClick={analyzeFile}
              disabled={!pdfFiles.length || loading}
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>

          {analysis && (
            <>
              <div className="bg-white rounded-xl shadow-md p-6 mb-8 border border-gray-300">
                <h2 className="text-3xl font-semibold mb-5 text-center text-gray-800">
                  📊 Spending Summary
                </h2>
                <table className="w-full text-left border border-gray-300">
                  <thead>
                    <tr className="bg-blue-100 text-blue-800">
                      <th className="border border-gray-300 p-3">Category</th>
                      <th className="border border-gray-300 p-3">Amount (₹)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(analysis.summary).map(([category, amount], i) => (
                      <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                        <td className="p-3 border border-gray-200 text-gray-700">{category}</td>
                        <td className="p-3 border border-gray-200 text-gray-700">₹{amount.toFixed(2)}</td>
                      </tr>
                    ))}
                    <tr className="bg-blue-50 font-bold">
                      <td className="p-3 border-t text-gray-800">Total</td>
                      <td className="p-3 border-t text-gray-800">₹{totalAmount.toFixed(2)}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="bg-white rounded-xl shadow-md p-6 border border-gray-300">
                <h2 className="text-3xl font-semibold mb-5 text-center text-gray-800">
                  📋 Transaction Details
                </h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border border-gray-300">
                    <thead>
                      <tr className="bg-blue-100 text-blue-800">
                        <th className="border border-gray-300 p-3">Date</th>
                        <th className="border border-gray-300 p-3">Merchant</th>
                        <th className="border border-gray-300 p-3">Amount</th>
                        <th className="border border-gray-300 p-3">Category</th>
                        <th className="border border-gray-300 p-3">Bank</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysis.transactions.map((txn, i) => (
                        <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
                          <td className="p-3 border border-gray-200 text-gray-700">{txn.date}</td>
                          <td className="p-3 border border-gray-200 text-gray-700">{txn.merchant}</td>
                          <td className="p-3 border border-gray-200 text-gray-700">₹{txn.amount}</td>
                          <td className="p-3 border border-gray-200 text-gray-700">{txn.category}</td>
                          <td className="p-3 border border-gray-200 text-gray-700">{txn.bank}</td>
                        </tr>
                      ))}
                      <tr className="bg-blue-50 font-bold">
                        <td colSpan="2" className="p-3 border-t text-gray-800">Total</td>
                        <td className="p-3 border-t text-gray-800">₹{totalAmount.toFixed(2)}</td>
                        <td className="p-3 border-t" colSpan="2"></td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white shadow py-4 text-center text-sm text-gray-500">
        © {new Date().getFullYear()} Credit Analyzer · Built with ❤️
      </footer>
    </div>
  );
}
