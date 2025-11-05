"use client";

import { useState } from "react";
import ConfigPanel from "@/components/ConfigPanel";
import ChartDisplay from "@/components/ChartDisplay";

export default function Home() {
  const [data, setData] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState({
    country: "UK",
    metric: "mtr",
    view: "absolute",
    maxChildren: 3,
    year: 2025,
    region: "LONDON",
    rent: 12000,
    childcarePerChild: 12000,
  });

  const handleCalculate = async (newConfig: any) => {
    setLoading(true);
    setConfig(newConfig);

    try {
      const endpoint = newConfig.country === "US" ? "/calculate/us" : "/calculate/uk";
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          max_children: newConfig.maxChildren,
          year: newConfig.year,
          metric: newConfig.metric,
          view: newConfig.view,
          ...(newConfig.country === "UK" ? {
            region: newConfig.region,
            rent: newConfig.rent,
            childcare_per_child: newConfig.childcarePerChild,
          } : {
            marital_status: newConfig.maritalStatus,
            state_code: newConfig.stateCode,
            spouse_income: newConfig.spouseIncome,
            include_health_benefits: newConfig.includeHealthBenefits,
          }),
        }),
      });

      const result = await response.json();
      setData(result.data);
    } catch (error) {
      console.error("Calculation error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white font-inter">
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-semibold text-[#319795]">
            The Marginal Child
          </h1>
          <p className="mt-2 text-gray-600">
            Analyze marginal tax rates and benefits by number of children
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-1">
            <ConfigPanel onCalculate={handleCalculate} initialConfig={config} />
          </div>

          <div className="lg:col-span-3">
            {loading && (
              <div className="flex items-center justify-center h-96">
                <div className="text-lg text-gray-500">Calculating...</div>
              </div>
            )}

            {!loading && data && data.length > 0 && (
              <ChartDisplay data={data} config={config} />
            )}

            {!loading && !data && (
              <div className="flex items-center justify-center h-96 text-gray-400">
                Configure options and click Calculate
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="mt-16 border-t border-gray-200 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-gray-600">
          Powered by <span className="font-semibold text-[#319795]">PolicyEngine</span>
        </div>
      </footer>
    </div>
  );
}
