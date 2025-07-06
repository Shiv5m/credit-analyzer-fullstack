// Your React component code (CreditAnalyzer) will go here
import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

export default function CreditAnalyzer() {
  const [pdfFile, setPdfFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const analyzeFile = async () => {
    const formData = new FormData();
    formData.append("file", pdfFile);

    try {
      const res = await fetch(import.meta.env.VITE_API_URL + "/analyze", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setAnalysis(data);
    } catch (error) {
      console.error("Analysis failed:", error);
      alert("Failed to analyze the PDF. Check if backend is running.");
    }
  };

  const renderChart = () => {
    const labels = Object.keys(analysis.summary);
    const data = Object.values(analysis.summary);

    return (
      <Pie
        data={{
          labels,
          datasets: [
            {
              label: "Spends by Category",
              data,
              backgroundColor: [
                "#f87171",
                "#60a5fa",
                "#34d399",
                "#fbbf24",
                "#c084fc",
              ],
            },
          ],
        }}
      />
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Credit Card Spend Analyzer</h1>

      <Card className="p-4 mb-6">
        <input type="file" accept="application/pdf" onChange={(e) => setPdfFile(e.target.files[0])} />
        <Button className="mt-2" onClick={analyzeFile} disabled={!pdfFile}>
          Analyze
        </Button>
      </Card>

      {analysis && (
        <>
          <Card className="mb-6">
            <CardContent>
              <h2 className="text-xl font-semibold mb-2">Spending Summary</h2>
              {renderChart()}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <h2 className="text-xl font-semibold mb-2">Transactions</h2>
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr>
                    <th className="border-b p-2">Date</th>
                    <th className="border-b p-2">Merchant</th>
                    <th className="border-b p-2">Amount</th>
                    <th className="border-b p-2">Category</th>
                  </tr>
                </thead>
                <tbody>
                  {analysis.transactions.map((txn, i) => (
                    <tr key={i}>
                      <td className="p-2 border-b">{txn.date}</td>
                      <td className="p-2 border-b">{txn.merchant}</td>
                      <td className="p-2 border-b">₹{txn.amount}</td>
                      <td className="p-2 border-b">{txn.category}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
